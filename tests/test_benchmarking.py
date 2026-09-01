import asyncio
import json
from pathlib import Path

import pytest

from agrofield_agent.benchmarking import (
    ERROR_CODES,
    REFERENCE_FIELDS,
    cohens_kappa,
    load_cases,
    reviewer_agreement,
    task_review_metrics,
)
from agrofield_agent.evaluate import run


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DATASET = ROOT / "benchmark" / "agronomy_blind_v1" / "data" / "cases.jsonl"
LEGACY_DATASET = ROOT / "fixtures" / "eval_cases.jsonl"


def _fields(**overrides):
    values = {name: None for name in REFERENCE_FIELDS}
    values.update(event_type="unknown")
    values.update(overrides)
    return {
        name: {"value": value, "evidence_quote": None, "conflict": False}
        for name, value in values.items()
    }


def _annotation(reviewer_id: str, *, missing=None, access_safe=True):
    return {
        "case_id": "case-1",
        "review_id": f"review-{reviewer_id}",
        "reviewer_id": reviewer_id,
        "review_origin": "human",
        "blind": True,
        "consent_to_anonymous_results": True,
        "reference_fields": _fields(
            crop_stage="V3", event_type="flooding", access_safe=access_safe
        ),
        "expected_missing": missing or [],
    }


def test_candidate_dataset_shape_split_and_privacy_status():
    cases = load_cases(CANDIDATE_DATASET)
    assert len(cases) == 30
    assert sum(case["split"] == "development" for case in cases) == 20
    assert sum(case["split"] == "holdout" for case in cases) == 10
    assert sum(case["double_review_required"] for case in cases) == 10
    assert sum(bool(case["legacy_id"]) for case in cases) == 12
    assert all(case["human_review_status"] == "candidate" for case in cases)
    assert all(case["privacy_status"] == "synthetic_no_real_data" for case in cases)
    assert all(
        case["field"]["latitude"] == 0 and case["field"]["longitude"] == 0
        for case in cases
    )
    assert all(
        set(case["candidate_reference"]["fields"]) == set(REFERENCE_FIELDS)
        for case in cases
    )


def test_cohens_kappa_and_raw_disagreement_are_reported():
    assert cohens_kappa(["yes", "no"], ["yes", "no"]) == 1.0
    assert cohens_kappa([], []) is None
    agreement = reviewer_agreement(
        [
            _annotation("R01", missing=["sample_points"]),
            _annotation("R02", missing=["sample_points", "crop_stage"]),
        ],
        [],
    )
    assert agreement["status"] == "available"
    assert agreement["double_annotated_case_pairs"] == 1
    assert agreement["raw_disagreement"] > 0
    assert agreement["missing_critical"]["cohens_kappa"] is not None


def test_task_precision_ignores_nonhuman_or_nonconsented_records():
    base = {
        "case_id": "case-1",
        "packet_id": "packet-1",
        "reviewer_id": "R01",
        "blind": True,
        "consent_to_anonymous_results": True,
        "task_labels": [{"task_index": 0, "classification": "appropriate"}],
    }
    rejected = task_review_metrics([{**base, "review_origin": "ai"}])
    assert rejected["task_precision"] is None
    assert rejected["invalid_or_nonhuman_records_ignored"] == 1
    accepted = task_review_metrics(
        [{**base, "review_origin": "human"}], {"case-1": 1}
    )
    assert accepted["task_precision"] == 1.0
    assert accepted["complete"] is True


def test_legacy_baseline_metrics_are_preserved_and_labeled():
    result = asyncio.run(run(LEGACY_DATASET))
    assert result["cases"] == 12
    assert result["extraction_precision"] == 0.9884
    assert result["extraction_recall"] == 0.9239
    assert result["extraction_micro_f1"] == 0.9551
    assert result["critical_omission_recall"] == 1.0
    assert result["unsupported_assertion_rate"] == 0.0
    assert result["decision_gate_safety"] == 1.0
    assert result["priority_ndcg"] == 1.0
    assert result["provider"] == "local/deterministic-es-v0.1"
    assert result["reference_status"] == "synthetic_local_fixture_reference"
    assert result["benchmark_validated"] is False


def test_candidate_evaluation_exposes_missing_human_validation():
    result = asyncio.run(run(CANDIDATE_DATASET))
    assert result["cases"] == 30
    assert result["reference_status"] == "provisional_candidate_reference"
    assert result["human_review_readiness"] == {
        "required_primary_cases": 30,
        "primary_reviewed_cases": 0,
        "required_double_review_cases": 10,
        "double_reviewed_cases": 0,
        "complete": False,
        "invalid_or_nonhuman_records_ignored": 0,
    }
    assert result["task_precision"] is None
    assert result["benchmark_validated"] is False
    assert set(result["error_matrix"]) == set(ERROR_CODES)
    assert result["adverse_failure_count"] > 0


def _nested_keys(value):
    if isinstance(value, dict):
        return set(value) | set().union(*(_nested_keys(item) for item in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_nested_keys(item) for item in value), set())
    return set()


def test_reference_and_output_packets_are_physically_separate(tmp_path: Path):
    reference_path = tmp_path / "phase-a-reference.jsonl"
    output_path = tmp_path / "phase-b-output.jsonl"
    result = asyncio.run(
        run(
            CANDIDATE_DATASET,
            split="holdout",
            reference_packet_out=reference_path,
            output_packet_out=output_path,
            system_alias="system-k7",
        )
    )
    reference_packets = [
        json.loads(line) for line in reference_path.read_text(encoding="utf-8").splitlines()
    ]
    output_packets = [
        json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()
    ]
    assert result["reference_packet"]["packets"] == 10
    assert result["output_packet"]["packets"] == 10
    assert len(reference_packets) == len(output_packets) == 10

    forbidden_phase_a = {
        "output",
        "system_alias",
        "provider",
        "split",
        "candidate_reference",
        "priority_score",
        "proposed_tasks",
        "telemetry",
    }
    assert all(packet["packet_type"] == "reference_annotation" for packet in reference_packets)
    assert all(not (_nested_keys(packet) & forbidden_phase_a) for packet in reference_packets)
    assert all(packet["packet_type"] == "output_review" for packet in output_packets)
    assert all("output" in packet and packet["system_alias"] == "system-k7" for packet in output_packets)
    assert {
        packet["packet_id"] for packet in reference_packets
    } == {
        packet["reference_packet_id"] for packet in output_packets
    }
    for packet in [*reference_packets, *output_packets]:
        serialized = json.dumps(packet)
        assert "provider" not in serialized
        assert "split" not in packet
        assert "latitude" not in serialized
        assert "longitude" not in serialized


def test_phase_packets_cannot_share_an_output_path(tmp_path: Path):
    same_path = tmp_path / "same.jsonl"
    with pytest.raises(ValueError, match="different files"):
        asyncio.run(
            run(
                CANDIDATE_DATASET,
                reference_packet_out=same_path,
                output_packet_out=same_path,
            )
        )
