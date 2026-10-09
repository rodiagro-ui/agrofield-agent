"""Capped batch run of synthetic development notes through the guarded contract.

Without the exact confirmation it only prints the plan and exits 2 with no
network access. Each note is one guarded request with zero retries; the batch
stops before a request whose worst case would exceed the total cap. Holdout
cases are refused. Results describe one model on synthetic references written
by a developer or an AI: a development diagnostic, never a validated benchmark.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx

from agrofield_agent.config import DEFAULT_NEBIUS_BASE_URL
from agrofield_agent.extraction_contract import EVIDENCE_FIELDS, PROFILE_ID
from agrofield_agent.nebius_smoke import (
    DEFAULT_MODEL,
    ContractViolation,
    PreflightBlocked,
    SmokePlan,
    UpstreamRequestFailure,
    _decimal_argument,
    _money,
    execute_one_request,
    preflight,
)
from agrofield_agent.services.extraction import LocalExtractionProvider

BATCH_CONFIRMATION_PHRASE = "RUN_NEBIUS_EVAL_BATCH"
LABELS = ("correct_observed", "correct_absent", "missing", "wrong_value", "unsupported")


def load_cases(path: Path) -> list[dict[str, Any]]:
    """Normalize the two synthetic development schemas; refuse anything else."""
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("split") == "holdout":
            raise PreflightBlocked("holdout cases must not be used for development runs")
        reference = row.get("expected") or row.get("gold")
        case_id = row.get("case_id") or row.get("id")
        if not isinstance(reference, dict) or not case_id or not set(reference) <= set(
            EVIDENCE_FIELDS
        ):
            raise PreflightBlocked("unsupported dataset schema for a development run")
        cases.append({
            "case_id": case_id,
            "focus": row.get("focus") or row.get("scenario"),
            "note": row["note"],
            "reference": reference,
            "reference_origin": row.get("reference_origin")
            or "synthetic_developer_reference_not_human_validated",
        })
    if not cases or len({case["case_id"] for case in cases}) != len(cases):
        raise PreflightBlocked("dataset must contain unique, nonempty cases")
    return cases


def compare(observation: dict[str, Any], reference: dict[str, Any]) -> dict[str, Any]:
    """Same labels as smoke_audit.compare_fields, over the reference's own fields."""
    counts = dict.fromkeys(LABELS, 0)
    errors = []
    for name in EVIDENCE_FIELDS:
        if name not in reference:
            continue
        truth, value = reference[name], observation.get(name)
        truth_missing, value_missing = truth in (None, "unknown"), value in (None, "unknown")
        if truth_missing and value_missing:
            label = "correct_absent"
        elif truth_missing:
            label = "unsupported"
        elif value_missing:
            label = "missing"
        elif value == truth and isinstance(value, bool) == isinstance(truth, bool):
            label = "correct_observed"
        else:
            label = "wrong_value"
        counts[label] += 1
        if label in {"missing", "wrong_value", "unsupported"}:
            errors.append({"field": name, "kind": label, "expected": truth, "observed": value})
    return {"fields": len(reference), **counts, "errors": errors}


def aggregate(comparisons: list[dict[str, Any]], rejected: list[dict[str, Any]]) -> dict[str, Any]:
    """Micro metrics; a rejected response contributes every expected fact as missed."""
    totals = {label: sum(item[label] for item in comparisons) for label in LABELS}
    lost = sum(
        1 for reference in rejected for value in reference.values()
        if value not in (None, "unknown")
    )
    correct = totals["correct_observed"]
    asserted = correct + totals["wrong_value"] + totals["unsupported"]
    expected = correct + totals["wrong_value"] + totals["missing"] + lost
    precision = correct / asserted if asserted else None
    recall = correct / expected if expected else None
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision and recall else (0.0 if asserted or expected else None)
    )
    return {
        **totals,
        "expected_facts_lost_to_rejected_responses": lost,
        "precision": None if precision is None else round(precision, 4),
        "recall": None if recall is None else round(recall, 4),
        "micro_f1": None if f1 is None else round(f1, 4),
        "unsupported_assertion_rate": round(totals["unsupported"] / asserted, 4)
        if asserted else None,
        "cases_with_all_fields_right": sum(1 for item in comparisons if not item["errors"]),
    }


def _percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return round(ordered[min(len(ordered) - 1, int(fraction * len(ordered)))], 1)


async def local_baseline(cases: list[dict[str, Any]]) -> dict[str, Any]:
    provider = LocalExtractionProvider()
    comparisons = []
    for case in cases:
        draft, _ = await provider.extract(case["note"])
        comparisons.append(compare(draft.model_dump(), case["reference"]))
    return {"provider": "local/deterministic-es-v0.1", **aggregate(comparisons, [])}


def plan_batch(
    cases: list[dict[str, Any]], plan: SmokePlan, max_total_cost_usd: Decimal
) -> dict[str, Any]:
    ceilings = [preflight(case["note"], plan)[1].estimated_cost_ceiling_usd for case in cases]
    return {
        "cases": len(cases),
        "per_request_cost_ceiling_usd": _money(max(ceilings)),
        "worst_case_total_usd": _money(sum(ceilings, Decimal(0))),
        "max_total_cost_usd": _money(max_total_cost_usd),
        "automatic_retries": 0,
    }


async def run_batch(
    cases: list[dict[str, Any]],
    plan: SmokePlan,
    api_key: str,
    max_total_cost_usd: Decimal,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    spent = Decimal(0)
    records: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    latencies: list[float] = []
    tokens = {"input": 0, "output": 0}
    stop_reason = "completed"
    for case in cases:
        ceiling = preflight(case["note"], plan)[1].estimated_cost_ceiling_usd
        if spent + ceiling > max_total_cost_usd:
            stop_reason = "total_cost_cap_would_be_exceeded"
            break
        record: dict[str, Any] = {"case_id": case["case_id"], "focus": case["focus"]}
        try:
            result = await execute_one_request(
                case["note"], plan, api_key, transport=transport
            )
        except ContractViolation as exc:
            # Charge what was reported; fall back to the ceiling when it was not.
            usage = exc.diagnostics
            reported = (usage.get("prompt_tokens"), usage.get("completion_tokens"))
            spent += ceiling if None in reported else (
                Decimal(reported[0]) * plan.input_price_per_million
                + Decimal(reported[1]) * plan.output_price_per_million
            ) / Decimal(1_000_000)
            record.update({"status": "contract_rejected", "failure_code": exc.code,
                           "safe_diagnostics": exc.diagnostics})
            rejected.append(case["reference"])
            records.append(record)
            continue
        except UpstreamRequestFailure as exc:
            spent += ceiling
            record.update({"status": "upstream_failed", "failure_code": exc.code,
                           "safe_diagnostics": exc.diagnostics})
            records.append(record)
            stop_reason = "upstream_failure_no_retry"
            break
        spent += Decimal(result["estimated_usage_cost_usd"])
        telemetry = result["telemetry"]
        comparison = compare(result["observation"], case["reference"])
        comparisons.append(comparison)
        latencies.append(telemetry["latency_ms"])
        tokens["input"] += telemetry["input_tokens"]
        tokens["output"] += telemetry["output_tokens"]
        record.update({
            "status": "accepted", "comparison": comparison,
            "observation": result["observation"], "telemetry": telemetry,
            "estimated_usage_cost_usd": result["estimated_usage_cost_usd"],
        })
        records.append(record)
    return {
        "scope": "synthetic_development_batch_not_a_validated_benchmark",
        "extraction_profile": PROFILE_ID,
        "model": plan.model,
        "benchmark_validated": False,
        "human_reviews": 0,
        "reference_origins": sorted({case["reference_origin"] for case in cases}),
        "stop_reason": stop_reason,
        "cases_in_dataset": len(cases),
        "requests_sent": len(records),
        "accepted": len(comparisons),
        "contract_rejected": len(rejected),
        "automatic_retries": 0,
        "nebius": aggregate(comparisons, rejected),
        "local_baseline_same_cases": await local_baseline(cases[: len(records)]),
        "latency_ms_p50": _percentile(latencies, 0.5),
        "latency_ms_p95": _percentile(latencies, 0.95),
        "latency_ms_mean": round(statistics.fmean(latencies), 1) if latencies else None,
        "input_tokens": tokens["input"],
        "output_tokens": tokens["output"],
        "estimated_total_cost_usd": _money(spent),
        "estimated_cost_per_accepted_note_usd": _money(spent / len(comparisons))
        if comparisons else None,
        "warning": "Synthetic references are not agronomist-validated. A literal quote "
        "does not prove semantic support. Do not report as benchmark performance.",
        "records": records,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset", type=Path, default=Path("fixtures/development/semantic_v2/cases.jsonl")
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--input-price-per-million", type=_decimal_argument, required=True)
    parser.add_argument("--output-price-per-million", type=_decimal_argument, required=True)
    parser.add_argument("--max-cost-per-request-usd", type=_decimal_argument,
                        default=Decimal("0.01"))
    parser.add_argument("--max-total-cost-usd", type=_decimal_argument, required=True)
    parser.add_argument("--max-requests", type=int, required=True)
    parser.add_argument("--confirm-live",
                        help=f"exactly {BATCH_CONFIRMATION_PHRASE}; omit for the plan only")
    parser.add_argument("--report", type=Path, help="write the sanitized report here")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        cases = load_cases(args.dataset)
        if not 1 <= args.max_requests <= 200:
            raise PreflightBlocked("--max-requests must be between 1 and 200")
        cases = cases[: args.max_requests]
        plan = SmokePlan(
            model=args.model, base_url=DEFAULT_NEBIUS_BASE_URL,
            max_completion_tokens=1024, prompt_token_budget=16384,
            input_price_per_million=args.input_price_per_million,
            output_price_per_million=args.output_price_per_million,
            max_cost_usd=args.max_cost_per_request_usd,
        )
        summary = plan_batch(cases, plan, args.max_total_cost_usd)
        print(json.dumps({"status": "plan", "network_request_sent": False, **summary}, indent=2))
        if args.confirm_live != BATCH_CONFIRMATION_PHRASE:
            raise PreflightBlocked(
                f"batch blocked; pass --confirm-live {BATCH_CONFIRMATION_PHRASE} only "
                "after the owner authorizes this request count and cap"
            )
        api_key = os.getenv("NEBIUS_API_KEY", "")
        if not api_key.strip():
            raise PreflightBlocked("NEBIUS_API_KEY is required for a live batch")
        report = asyncio.run(run_batch(cases, plan, api_key, args.max_total_cost_usd))
    except PreflightBlocked as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False))
        return 2
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(serialized + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "records"},
                     ensure_ascii=False, indent=2))
    return 0 if report["stop_reason"] == "completed" else 3


if __name__ == "__main__":
    raise SystemExit(main())
