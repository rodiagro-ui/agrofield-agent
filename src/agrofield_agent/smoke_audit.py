"""Offline, single-note audit of a saved live observation, never an API runner."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

from agrofield_agent.nebius_smoke import EVIDENCE_FIELDS
from agrofield_agent.services.extraction import LocalExtractionProvider


def compare_fields(observation: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    if set(expected) != set(EVIDENCE_FIELDS) or not set(expected) <= set(observation):
        raise ValueError("A complete 12-field reference and observation are required")
    counts = {name: 0 for name in ("correct_observed", "correct_absent", "missing", "wrong_value", "unsupported")}
    errors = []
    for field in EVIDENCE_FIELDS:
        truth, value = expected[field], observation[field]
        truth_missing, value_missing = truth in (None, "unknown"), value in (None, "unknown")
        if truth_missing and value_missing:
            label = "correct_absent"
        elif truth_missing:
            label = "unsupported"
        elif value_missing:
            label = "missing"
        elif value == truth and (isinstance(value, bool) == isinstance(truth, bool)):
            label = "correct_observed"
        else:
            label = "wrong_value"
        counts[label] += 1
        if label in {"missing", "wrong_value", "unsupported"}:
            errors.append({"field": field, "kind": label, "expected": truth, "observed": value})
    return {"fields": len(EVIDENCE_FIELDS), **counts, "errors": errors}


async def audit(note: str, saved: dict[str, Any], reference: dict[str, Any]) -> dict[str, Any]:
    digest = hashlib.sha256(note.strip().encode("utf-8")).hexdigest()
    if any(item.get("normalized_note_sha256") != digest for item in (saved, reference)):
        raise ValueError("Saved response/reference does not match the input note")
    if saved.get("status") != "live_route_contract_pass" or saved.get("http_status") != 200:
        raise ValueError("An accepted saved observation is required")
    local, telemetry = await LocalExtractionProvider().extract(note)
    observation = saved["observation"]
    expected = reference["expected"]
    nonempty_quotes = [quote for quote in observation["evidence_quotes"].values() if quote]
    return {
        "scope": "single_synthetic_development_note_diagnostic",
        "cases": 1,
        "network_request_sent": False,
        "benchmark_validated": False,
        "reference_status": reference["reference_status"],
        "local_provider": f"{telemetry.provider}/{telemetry.model}",
        "saved_live_model": saved["model"],
        "saved_request_id": saved["telemetry"]["request_id"],
        "local": compare_fields(local.model_dump(), expected),
        "saved_nebius": compare_fields(observation, expected),
        "saved_quote_literal_fraction": sum(quote in note for quote in nonempty_quotes) / len(nonempty_quotes) if nonempty_quotes else None,
        "warning": "A literal quote does not prove semantic support. One synthetic development note does not establish benchmark performance or model superiority.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--note", type=Path, default=Path("fixtures/nebius_smoke_note.txt"))
    parser.add_argument("--reference", type=Path, default=Path("fixtures/nebius_smoke_reference.json"))
    parser.add_argument("--saved", type=Path, default=Path("docs/submission/evidence/nebius-source-anchor-smoke-2026-09-14.json"))
    args = parser.parse_args()
    result = asyncio.run(audit(
        args.note.read_text(encoding="utf-8"),
        json.loads(args.saved.read_text(encoding="utf-8")),
        json.loads(args.reference.read_text(encoding="utf-8")),
    ))
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
