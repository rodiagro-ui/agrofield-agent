from __future__ import annotations

import argparse
import asyncio
import json
import math
import statistics
from pathlib import Path
from typing import Any

from agrofield_agent.models import FieldRecord, StructuredObservation
from agrofield_agent.policy import evaluate_policy
from agrofield_agent.services.extraction import LocalExtractionProvider


FIELDS = [
    "crop_stage",
    "event_type",
    "event_hours_ago",
    "access_safe",
    "sample_points",
    "affected_area_pct",
    "standing_water_pct",
    "water_duration_hours",
    "lodging_pct",
    "stem_damage_pct",
    "stand_count_per_m",
]


def _equal(predicted: Any, gold: Any) -> bool:
    if isinstance(gold, (int, float)) and isinstance(predicted, (int, float)):
        return math.isclose(float(predicted), float(gold), abs_tol=0.01)
    return predicted == gold


def _dcg(relevances: list[float]) -> float:
    return sum((2**rel - 1) / math.log2(index + 2) for index, rel in enumerate(relevances))


async def run(path: Path) -> dict[str, Any]:
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    provider = LocalExtractionProvider()
    tp = fp = fn = unsupported = predicted_non_null = 0
    omission_tp = omission_fn = safe_blocks = unsafe_missing_cases = 0
    latencies: list[float] = []
    groups: dict[str, list[tuple[float, float]]] = {}

    for case in cases:
        draft, telemetry = await provider.extract(case["note"])
        latencies.append(telemetry.latency_ms)
        observation = StructuredObservation(
            **draft.model_dump(),
            field_id=case["field"]["id"],
            raw_text=case["note"],
            provider="local",
        )
        field = FieldRecord.model_validate(case["field"])
        status, missing, _, score, _, _ = evaluate_policy(field, observation)
        gold = case["gold"]
        for name in FIELDS:
            pred = getattr(observation, name)
            expected = gold.get(name)
            if pred is not None and pred != "unknown":
                predicted_non_null += 1
            if expected is None:
                if pred is not None and pred != "unknown":
                    fp += 1
                    unsupported += 1
            elif pred is None or pred == "unknown":
                fn += 1
            elif _equal(pred, expected):
                tp += 1
            else:
                fp += 1
                fn += 1

        expected_missing = set(case.get("expected_missing", []))
        actual_missing = set(missing)
        omission_tp += len(expected_missing & actual_missing)
        omission_fn += len(expected_missing - actual_missing)
        if expected_missing:
            unsafe_missing_cases += 1
            safe_blocks += int(status == "blocked")
        if case.get("scenario"):
            groups.setdefault(case["scenario"], []).append(
                (score, float(case["priority_relevance"]))
            )

    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    omission_recall = omission_tp / (omission_tp + omission_fn) if omission_tp + omission_fn else 1.0
    ndcgs: list[float] = []
    for pairs in groups.values():
        ranked = [rel for _, rel in sorted(pairs, reverse=True)]
        ideal = sorted((rel for _, rel in pairs), reverse=True)
        ndcgs.append(_dcg(ranked) / _dcg(ideal) if _dcg(ideal) else 1.0)

    return {
        "cases": len(cases),
        "extraction_precision": round(precision, 4),
        "extraction_recall": round(recall, 4),
        "extraction_micro_f1": round(f1, 4),
        "critical_omission_recall": round(omission_recall, 4),
        "unsupported_assertion_rate": round(unsupported / predicted_non_null, 4) if predicted_non_null else 0.0,
        "decision_gate_safety": round(safe_blocks / unsafe_missing_cases, 4) if unsafe_missing_cases else 1.0,
        "priority_ndcg": round(statistics.mean(ndcgs), 4) if ndcgs else None,
        "latency_ms_p50": round(statistics.median(latencies), 3),
        "latency_ms_max": round(max(latencies), 3),
        "provider": "local/deterministic-es-v0.1",
        "estimated_cost_usd": 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate AgroField extraction and policy")
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.dataset)), indent=2))


if __name__ == "__main__":
    main()
