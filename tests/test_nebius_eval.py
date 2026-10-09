import asyncio
import json
from decimal import Decimal

import httpx
import pytest

from agrofield_agent import nebius_eval
from agrofield_agent.app import PROJECT_ROOT
from agrofield_agent.config import DEFAULT_NEBIUS_BASE_URL
from agrofield_agent.nebius_eval import (
    BATCH_CONFIRMATION_PHRASE,
    aggregate,
    compare,
    load_cases,
    run_batch,
)
from agrofield_agent.nebius_smoke import DEFAULT_MODEL, PreflightBlocked, SmokePlan


DEV = PROJECT_ROOT / "fixtures" / "development" / "semantic_v2" / "cases.jsonl"
LEGACY = PROJECT_ROOT / "fixtures" / "eval_cases.jsonl"
SECRET = "eval-test-secret-not-a-credential"
RAW_DEV = [json.loads(line) for line in DEV.read_text(encoding="utf-8").splitlines() if line.strip()]
SMOKE_REFERENCE = json.loads(
    (PROJECT_ROOT / "fixtures" / "nebius_smoke_reference.json").read_text(encoding="utf-8")
)["expected"]


def plan():
    return SmokePlan(
        model=DEFAULT_MODEL, base_url=DEFAULT_NEBIUS_BASE_URL,
        max_completion_tokens=1024, prompt_token_budget=16384,
        input_price_per_million=Decimal("0.06"),
        output_price_per_million=Decimal("0.24"), max_cost_usd=Decimal("0.01"),
    )


def reference_arguments(index):
    """Arguments that satisfy the contract for development case `index`."""
    row = RAW_DEV[index]
    return {**row["expected"], "evidence_sources": row["evidence_sources"],
            "note_sources": row["note_sources"], "uncertainties": row["uncertainties"]}


def body(arguments):
    return {
        "id": "chatcmpl-eval-test",
        "choices": [{
            "finish_reason": "tool_calls",
            "message": {"role": "assistant", "content": None, "tool_calls": [{
                "id": "call", "type": "function",
                "function": {"name": "record_field_observation",
                             "arguments": json.dumps(arguments)},
            }]},
        }],
        "usage": {"prompt_tokens": 900, "completion_tokens": 120},
    }


def test_load_cases_accepts_both_synthetic_schemas_and_refuses_holdout(tmp_path):
    development = load_cases(DEV)
    legacy = load_cases(LEGACY)

    assert len(development) == 20 and len(legacy) == 12
    assert development[0]["reference_origin"] == "ai_authored_synthetic_not_human_validated"
    assert set(legacy[0]["reference"]) < set(nebius_eval.EVIDENCE_FIELDS)

    holdout = tmp_path / "holdout.jsonl"
    holdout.write_text(json.dumps({"id": "H1", "split": "holdout", "note": "x",
                                   "gold": {"crop_stage": "V3"}}) + "\n", encoding="utf-8")
    with pytest.raises(PreflightBlocked, match="holdout"):
        load_cases(holdout)


def test_compare_matches_smoke_audit_labels():
    observation = {**SMOKE_REFERENCE, "event_type": "mixed", "event_hours_ago": None,
                   "general_condition": "mixed"}
    result = compare(observation, SMOKE_REFERENCE)
    assert (result["correct_observed"], result["missing"], result["wrong_value"],
            result["unsupported"]) == (6, 1, 1, 1)


def test_aggregate_counts_rejected_responses_as_lost_recall():
    accepted = compare(SMOKE_REFERENCE, SMOKE_REFERENCE)
    result = aggregate([accepted], [SMOKE_REFERENCE])
    assert result["precision"] == 1.0
    assert result["recall"] == 0.5
    assert result["expected_facts_lost_to_rejected_responses"] == 8


def test_batch_sends_one_request_per_case_and_stops_at_the_total_cap():
    cases = load_cases(DEV)[:4]
    calls = []

    def endpoint(request):
        calls.append(json.loads(request.content)["messages"][1]["content"])
        return httpx.Response(200, json=body(reference_arguments(len(calls) - 1)))

    # Two settled requests (US$0.00008280 each) plus a third worst-case
    # ceiling of US$0.00122880 would exceed this cap; two fit.
    report = asyncio.run(run_batch(
        cases, plan(), SECRET, Decimal("0.00135"), transport=httpx.MockTransport(endpoint)
    ))

    assert len(calls) == 2 and len(set(calls)) == 2
    assert report["requests_sent"] == 2 and report["accepted"] == 2
    assert report["nebius"]["micro_f1"] == 1.0
    assert report["stop_reason"] == "total_cost_cap_would_be_exceeded"
    assert report["benchmark_validated"] is False
    assert report["local_baseline_same_cases"]["provider"] == "local/deterministic-es-v0.1"
    assert Decimal(report["estimated_total_cost_usd"]) == 2 * Decimal("0.00008280")
    assert SECRET not in json.dumps(report)


def test_contract_rejection_is_recorded_without_retry_and_upstream_failure_stops():
    cases = load_cases(DEV)[:3]
    responses = iter([
        httpx.Response(200, json=body({**reference_arguments(0), "note_sources": ["S99"]})),
        httpx.Response(200, json=body(reference_arguments(1))),
        httpx.Response(503, json={"error": "synthetic"}),
    ])
    calls = 0

    def endpoint(request):
        nonlocal calls
        calls += 1
        return next(responses)

    report = asyncio.run(run_batch(
        cases, plan(), SECRET, Decimal("1"), transport=httpx.MockTransport(endpoint)
    ))

    assert calls == 3
    assert [item["status"] for item in report["records"]] == [
        "contract_rejected", "accepted", "upstream_failed"]
    assert report["stop_reason"] == "upstream_failure_no_retry"
    assert report["contract_rejected"] == 1 and report["accepted"] == 1
    assert "arguments" not in json.dumps(report["records"][0])


@pytest.mark.parametrize("extra", [
    [],
    ["--confirm-live", "RUN_ONE_NEBIUS_REQUEST"],
    ["--confirm-live", BATCH_CONFIRMATION_PHRASE],
    ["--max-requests", "0"],
])
def test_cli_blocks_without_exact_confirmation_or_key(monkeypatch, capsys, extra):
    monkeypatch.chdir(PROJECT_ROOT)
    monkeypatch.delenv("NEBIUS_API_KEY", raising=False)
    monkeypatch.setattr(nebius_eval, "execute_one_request",
                        lambda *a, **k: pytest.fail("no network"))
    argv = ["--input-price-per-million", "0.06", "--output-price-per-million", "0.24",
            "--max-total-cost-usd", "0.05", "--max-requests", "20"]
    if extra[:1] == ["--max-requests"]:
        argv[-1] = extra[1]
        extra = []
    assert nebius_eval.main(argv + extra) == 2
    assert '"status": "blocked"' in capsys.readouterr().out
