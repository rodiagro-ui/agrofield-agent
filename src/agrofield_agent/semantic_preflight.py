"""Offline developer-reference and request-budget checks; never model evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from agrofield_agent.config import DEFAULT_NEBIUS_BASE_URL
from agrofield_agent.extraction_contract import EVIDENCE_FIELDS, PROFILE_ID
from agrofield_agent.freeze import canonical_sha256
from agrofield_agent.models import ObservationDraft
from agrofield_agent.nebius_smoke import (
    DEFAULT_MODEL, SmokePlan, _resolve_arguments, _validate_evidence,
    _validate_quantities, preflight,
)

DEFAULT_DATASET = Path("fixtures/development/semantic_v3/cases.jsonl")
REFERENCE_ORIGIN = "ai_authored_synthetic_not_human_validated"


def historical_plan() -> SmokePlan:
    """Arithmetic using 2026-09-14 prices; not current prices or authorization."""
    return SmokePlan(
        model=DEFAULT_MODEL, base_url=DEFAULT_NEBIUS_BASE_URL,
        max_completion_tokens=1024, prompt_token_budget=16384,
        input_price_per_million=Decimal("0.06"),
        output_price_per_million=Decimal("0.24"), max_cost_usd=Decimal("0.01"),
    )


def reference_arguments(case: dict[str, Any]) -> dict[str, Any]:
    """Construct a reference contract, never a fabricated model response."""
    if case.get("split") != "development" or case.get("reference_origin") != REFERENCE_ORIGIN:
        raise ValueError("Only explicitly AI-authored synthetic development references are allowed")
    if set(case["expected"]) != set(EVIDENCE_FIELDS):
        raise ValueError("Reference must explicitly include all 12 observation fields")
    return {
        **case["expected"],
        "evidence_sources": case["evidence_sources"],
        "note_sources": case["note_sources"],
        "uncertainties": case["uncertainties"],
    }


def check_cases(cases: list[dict[str, Any]], plan: SmokePlan) -> dict[str, Any]:
    if not cases:
        raise ValueError("Development set must not be empty")
    seen_ids: set[str] = set()
    seen_notes: set[str] = set()
    checks = []
    observed_counts = dict.fromkeys(EVIDENCE_FIELDS, 0)
    unknown_counts = dict.fromkeys(EVIDENCE_FIELDS, 0)
    for case in cases:
        case_id, note = case["case_id"], case["note"]
        if not isinstance(case_id, str) or not case_id.strip() or case_id in seen_ids:
            raise ValueError("Development case IDs must be nonempty and unique")
        note_digest = hashlib.sha256(note.strip().encode("utf-8")).hexdigest()
        if note_digest in seen_notes:
            raise ValueError("Development notes must be unique")
        seen_ids.add(case_id)
        seen_notes.add(note_digest)
        arguments = reference_arguments(case)
        draft = ObservationDraft.model_validate(_resolve_arguments(arguments, note), strict=True)
        _validate_quantities(draft)
        _validate_evidence(draft, note)
        payload, estimate = preflight(note, plan)
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for field_name in EVIDENCE_FIELDS:
            if case["expected"][field_name] in (None, "unknown"):
                unknown_counts[field_name] += 1
            else:
                observed_counts[field_name] += 1
        checks.append({
            "case_id": case_id, "focus": case["focus"],
            "normalized_note_sha256": note_digest,
            "request_payload_sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
            "reference_contract_valid": True,
            "cost_preflight": estimate.public_dict(),
        })
    return {
        "status": "development_reference_preflight_only",
        "extraction_profile": PROFILE_ID,
        "reference_origin": REFERENCE_ORIGIN,
        "cases": len(checks), "network_request_sent": False,
        "human_reviews": 0, "benchmark_validated": False,
        "nemotron_quality": None,
        "pricing_basis": "historical_2026-09-14_not_authorization",
        "max_serialized_request_bytes": max(c["cost_preflight"]["serialized_request_bytes"] for c in checks),
        "observed_reference_counts": observed_counts,
        "unknown_reference_counts": unknown_counts,
        "checks": checks,
        "warning": "Reference shape and literal quotes are checked, not agronomic correctness or model performance. No responses are generated or scored.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    cases = [json.loads(line) for line in args.dataset.read_text(encoding="utf-8").splitlines() if line.strip()]
    result = check_cases(cases, historical_plan())
    result["dataset_canonical_sha256"] = canonical_sha256(args.dataset)
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
