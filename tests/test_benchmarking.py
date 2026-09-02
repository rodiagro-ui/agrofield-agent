import asyncio
import json
from pathlib import Path

import pytest

from agrofield_agent.benchmarking import (
    ERROR_CODES,
    REFERENCE_FIELDS,
    SCHEMA_VERSION,
    adjudication_readiness,
    cohens_kappa,
    human_case_annotations,
    human_output_reviews,
    interview_readiness,
    load_cases,
    output_packet_id,
    record_sha256,
    reference_packet_id,
    review_readiness,
    reviewer_agreement,
    task_review_metrics,
)
from agrofield_agent.evaluate import run


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DATASET = ROOT / "benchmark" / "agronomy_blind_v1" / "data" / "cases.jsonl"
LEGACY_DATASET = ROOT / "fixtures" / "eval_cases.jsonl"
TEMPLATES = ROOT / "benchmark" / "agronomy_blind_v1" / "templates"
TEST_NOTE = "Soja V3, anegamiento hace 18 horas, acceso seguro y 6 puntos."
TEST_CASE = {
    "id": "case-1",
    "note": TEST_NOTE,
    "ranking_group": "test-ranking-group",
    "double_review_required": True,
}


def _fields(**overrides):
    values = {name: None for name in REFERENCE_FIELDS}
    values.update(event_type="unknown")
    values.update(overrides)
    return {
        name: {
            "value": value,
            "evidence_quote": (
                TEST_NOTE if value is not None and value != "unknown" else None
            ),
            "conflict": False,
        }
        for name, value in values.items()
    }


def _annotation(
    reviewer_id: str,
    *,
    assignment: str = "primary",
    missing: list[str] | None = None,
    access_safe: bool = True,
    case: dict | None = None,
    possible_prior_exposure: bool = False,
):
    case = case or TEST_CASE
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case["id"],
        "packet_id": reference_packet_id(case["id"]),
        "review_id": f"review-{case['id']}-{reviewer_id.lower()}-{assignment}",
        "reviewer_id": reviewer_id,
        "review_origin": "human",
        "review_assignment": assignment,
        "reviewer_role": "agronomist",
        "experience_band": "5-9",
        "consent_to_anonymous_results": True,
        "blind": True,
        "possible_prior_exposure": possible_prior_exposure,
        "completed_at": "2026-09-01",
        "reference_fields": _fields(
            crop_stage="V3", event_type="flooding", access_safe=access_safe
        ),
        "expected_missing": missing or [],
        "priority_relevance": 3,
        "ranking_group": case["ranking_group"],
        "privacy_check": "passed",
    }


def _output_review(
    annotation: dict,
    *,
    classification: str = "appropriate",
    task_count: int = 1,
    possible_prior_exposure: bool = False,
):
    alias = "system-k7"
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": annotation["case_id"],
        "packet_id": output_packet_id(annotation["case_id"], alias),
        "reference_packet_id": reference_packet_id(annotation["case_id"]),
        "reference_lock_sha256": record_sha256(annotation),
        "system_alias": alias,
        "review_id": f"output-{annotation['reviewer_id'].lower()}-{annotation['review_assignment']}",
        "reviewer_id": annotation["reviewer_id"],
        "review_origin": "human",
        "review_assignment": annotation["review_assignment"],
        "consent_to_anonymous_results": True,
        "blind": True,
        "possible_prior_exposure": possible_prior_exposure,
        "completed_at": "2026-09-01",
        "privacy_check": "passed",
        "fact_support": "all_supported",
        "missing_critical_assessment": "correct",
        "priority_assessment": "justified",
        "task_labels": [
            {
                "task_index": index,
                "classification": classification,
                "rationale": "Clasificación completa del fixture de prueba.",
            }
            for index in range(task_count)
        ],
        "would_reduce_followup_messages": "yes",
        "would_reduce_return_visits": "uncertain",
        "errors": [],
        "overall_safety": "safe",
    }


def _adjudication(
    case: dict,
    annotations: list[dict],
    adjudicator_id: str,
):
    return {
        "schema_version": SCHEMA_VERSION,
        "adjudication_id": f"adjudication-{case['id']}",
        "case_id": case["id"],
        "status": "adjudicated",
        "adjudicator_id": adjudicator_id,
        "adjudication_origin": "human",
        "consent_to_anonymous_results": True,
        "source_review_ids": [item["review_id"] for item in annotations],
        "completed_at": "2026-09-01",
        "privacy_check": "passed",
        "final_reference_fields": annotations[0]["reference_fields"],
        "expected_missing": annotations[0]["expected_missing"],
        "priority_relevance": annotations[0]["priority_relevance"],
        "decisions": [
            {
                "target": "full-reference",
                "decision": "accept-reviewed-reference",
                "rationale": "Fixture para verificar independencia entre roles.",
            }
        ],
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


def test_cohens_kappa_and_raw_disagreement_are_reported_for_fixed_pair():
    assert cohens_kappa(["yes", "no"], ["yes", "no"]) == 1.0
    assert cohens_kappa([], []) is None
    primary = _annotation("R01", missing=["sample_points"])
    secondary = _annotation(
        "R02",
        assignment="secondary",
        missing=["sample_points", "crop_stage"],
    )
    agreement = reviewer_agreement(
        [TEST_CASE],
        [primary, secondary],
        [_output_review(primary), _output_review(secondary)],
        {TEST_CASE["id"]: 1},
    )
    assert agreement["status"] == "complete"
    assert agreement["double_annotated_case_pairs"] == 1
    assert agreement["double_reviewed_output_pairs"] == 1
    assert agreement["raw_disagreement"] > 0
    assert agreement["missing_critical"]["cohens_kappa"] is not None


def test_agreement_reports_sensitivity_without_prior_exposure():
    primary = _annotation("R01", missing=["sample_points"])
    secondary = _annotation(
        "R02",
        assignment="secondary",
        missing=["sample_points", "crop_stage"],
        possible_prior_exposure=True,
    )
    agreement = reviewer_agreement(
        [TEST_CASE],
        [primary, secondary],
        [
            _output_review(primary),
            _output_review(secondary, possible_prior_exposure=True),
        ],
        {TEST_CASE["id"]: 1},
    )

    assert agreement["complete"] is True
    assert agreement["raw_disagreement"] > 0
    assert agreement["exposure_sensitivity"][
        "binding_metrics_include_all_complete_pairs"
    ] is True
    for phase in ("reference", "output"):
        sensitivity = agreement["exposure_sensitivity"][phase]
        assert sensitivity["all_pair_count"] == 1
        assert sensitivity["without_possible_prior_exposure_pair_count"] == 0
        assert sensitivity["excluded_possible_prior_exposure_case_ids"] == [
            TEST_CASE["id"]
        ]


def test_reviewer_assignment_overlap_across_cases_blocks_readiness():
    second_case = {
        **TEST_CASE,
        "id": "case-2",
    }
    annotations = [
        _annotation("R01", case=TEST_CASE),
        _annotation("R02", assignment="secondary", case=TEST_CASE),
        _annotation("R02", case=second_case),
        _annotation("R03", assignment="secondary", case=second_case),
    ]

    readiness = review_readiness([TEST_CASE, second_case], annotations)

    assert readiness["reviewer_independence_failure_case_ids"] == []
    assert readiness["reviewer_assignment_overlap_ids"] == ["R02"]
    assert readiness["reviewer_role_independence_complete"] is False
    assert readiness["complete"] is False


def test_adjudicator_overlap_with_any_reviewer_blocks_role_independence():
    second_case = {
        **TEST_CASE,
        "id": "case-2",
        "double_review_required": False,
    }
    first_annotations = [
        _annotation("R01", case=TEST_CASE),
        _annotation("R02", assignment="secondary", case=TEST_CASE),
    ]
    second_annotations = [_annotation("R01", case=second_case)]
    status = adjudication_readiness(
        [TEST_CASE, second_case],
        [*first_annotations, *second_annotations],
        [
            _adjudication(TEST_CASE, first_annotations, "A01"),
            _adjudication(second_case, second_annotations, "R02"),
        ],
    )

    assert status["adjudicator_reviewer_overlap_case_ids"] == []
    assert status["reviewer_adjudicator_overlap_ids"] == ["R02"]
    assert status["role_independence_complete"] is False
    assert status["complete"] is False


def test_task_precision_uses_primary_only_and_rejects_nonhuman_records():
    primary = _annotation("R01")
    secondary = _annotation("R02", assignment="secondary")
    invalid = {**_output_review(primary), "review_origin": "ai"}
    rejected = task_review_metrics(
        [TEST_CASE], [invalid], {TEST_CASE["id"]: 1}, [primary, secondary]
    )
    assert rejected["task_precision"] is None
    assert rejected["invalid_or_nonhuman_records_ignored"] == 1

    accepted = task_review_metrics(
        [TEST_CASE],
        [_output_review(primary), _output_review(secondary, classification="unsafe")],
        {TEST_CASE["id"]: 1},
        [primary, secondary],
    )
    assert accepted["primary_task_precision"] == 1.0
    assert accepted["task_precision"] == 1.0
    assert accepted["secondary_task_review_counts"]["unsafe"] == 1
    assert accepted["complete"] is True


def test_adding_secondary_review_cannot_change_primary_task_precision():
    primary = _annotation("R01")
    secondary = _annotation("R02", assignment="secondary")
    without_secondary = task_review_metrics(
        [TEST_CASE],
        [_output_review(primary)],
        {TEST_CASE["id"]: 1},
        [primary, secondary],
    )
    with_secondary = task_review_metrics(
        [TEST_CASE],
        [_output_review(primary), _output_review(secondary, classification="unsafe")],
        {TEST_CASE["id"]: 1},
        [primary, secondary],
    )
    assert without_secondary["primary_task_precision"] == 1.0
    assert with_secondary["primary_task_precision"] == 1.0
    assert without_secondary["double_complete"] is False
    assert with_secondary["double_complete"] is True


def test_missing_secondary_output_is_named_and_blocks_completeness():
    primary = _annotation("R01")
    secondary = _annotation("R02", assignment="secondary")
    metrics = task_review_metrics(
        [TEST_CASE],
        [_output_review(primary)],
        {TEST_CASE["id"]: 1},
        [primary, secondary],
    )
    agreement = reviewer_agreement(
        [TEST_CASE],
        [primary, secondary],
        [_output_review(primary)],
        {TEST_CASE["id"]: 1},
    )
    assert metrics["complete"] is False
    assert metrics["missing_secondary_output_case_ids"] == [TEST_CASE["id"]]
    assert agreement["complete"] is False
    assert agreement["missing_output_pair_case_ids"] == [TEST_CASE["id"]]


def test_output_review_requires_the_matching_locked_phase_a_annotation():
    primary = _annotation("R01")
    secondary = _annotation("R02", assignment="secondary")
    tampered = {**_output_review(primary), "reference_lock_sha256": "0" * 64}
    metrics = task_review_metrics(
        [TEST_CASE],
        [tampered, _output_review(secondary)],
        {TEST_CASE["id"]: 1},
        [primary, secondary],
    )
    assert metrics["complete"] is False
    assert metrics["phase_a_lock_failure_case_ids"] == [TEST_CASE["id"]]


def test_uncompleted_templates_are_ignored_and_counted_invalid():
    annotation_template = json.loads(
        (TEMPLATES / "case-annotation.template.json").read_text(encoding="utf-8")
    )
    output_template = json.loads(
        (TEMPLATES / "output-review.template.json").read_text(encoding="utf-8")
    )
    interview_template = json.loads(
        (TEMPLATES / "interview-record.template.json").read_text(encoding="utf-8")
    )
    adjudication_template = json.loads(
        (TEMPLATES / "adjudication.template.json").read_text(encoding="utf-8")
    )
    assert human_case_annotations([annotation_template]) == []
    assert human_output_reviews([output_template]) == []
    assert review_readiness([TEST_CASE], [annotation_template])[
        "invalid_or_nonhuman_records_ignored"
    ] == 1
    assert task_review_metrics(
        [TEST_CASE], [output_template], {TEST_CASE["id"]: 1}, []
    )["invalid_or_nonhuman_records_ignored"] == 1
    assert adjudication_readiness([TEST_CASE], [], [adjudication_template])[
        "invalid_or_nonhuman_records_ignored"
    ] == 1
    assert interview_readiness([interview_template]) == {
        "required_minimum": 3,
        "allowed_maximum": 5,
        "valid_unique_interviews": 0,
        "duplicate_participant_ids": [],
        "roles": {},
        "experience_bands": {},
        "invalid_or_nonhuman_records_ignored": 1,
        "complete": False,
    }


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
    readiness = result["human_review_readiness"]
    assert readiness["required_primary_cases"] == 30
    assert readiness["primary_reviewed_cases"] == 0
    assert readiness["required_double_review_cases"] == 10
    assert readiness["double_reviewed_cases"] == 0
    assert len(readiness["missing_primary_case_ids"]) == 30
    assert len(readiness["missing_secondary_case_ids"]) == 10
    assert readiness["complete"] is False
    assert result["human_interview_readiness"]["valid_unique_interviews"] == 0
    assert result["human_freeze_readiness"]["complete"] is False
    assert result["task_precision"] is None
    assert result["benchmark_validated"] is False
    assert set(result["error_matrix"]) == set(ERROR_CODES)
    assert result["adverse_failure_count"] > 0


def _nested_keys(value):
    if isinstance(value, dict):
        return set(value) | set().union(
            *(_nested_keys(item) for item in value.values()), set()
        )
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
        json.loads(line)
        for line in reference_path.read_text(encoding="utf-8").splitlines()
    ]
    output_packets = [
        json.loads(line)
        for line in output_path.read_text(encoding="utf-8").splitlines()
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
    assert all(
        packet["packet_type"] == "reference_annotation"
        for packet in reference_packets
    )
    assert all(
        not (_nested_keys(packet) & forbidden_phase_a) for packet in reference_packets
    )
    assert all(packet["packet_type"] == "output_review" for packet in output_packets)
    assert all(
        "output" in packet and packet["system_alias"] == "system-k7"
        for packet in output_packets
    )
    assert {packet["packet_id"] for packet in reference_packets} == {
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
