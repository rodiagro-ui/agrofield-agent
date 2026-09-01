import asyncio
import json
from copy import deepcopy
from pathlib import Path

import pytest

from agrofield_agent.benchmarking import (
    REFERENCE_FIELDS,
    SCHEMA_VERSION,
    load_cases,
    output_packet_id,
    record_sha256,
    reference_packet_id,
)
from agrofield_agent.evaluate import build_validation_gates, main, run
from agrofield_agent.freeze import canonical_sha256
from agrofield_agent.models import FieldRecord, StructuredObservation
from agrofield_agent.policy import evaluate_policy
from agrofield_agent.services.extraction import LocalExtractionProvider


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DATASET = ROOT / "benchmark" / "agronomy_blind_v1" / "data" / "cases.jsonl"


def _passing_gate_inputs():
    cases = [
        {"id": f"fixture-{index:02d}", "double_review_required": index <= 10}
        for index in range(1, 31)
    ]
    return {
        "split": None,
        "cases": cases,
        "interviews": {
            "complete": True,
            "valid_unique_interviews": 3,
            "invalid_or_nonhuman_records_ignored": 0,
        },
        "readiness": {
            "complete": True,
            "primary_reviewed_cases": 30,
            "double_reviewed_cases": 10,
            "invalid_or_nonhuman_records_ignored": 0,
        },
        "task_metrics": {
            "complete": True,
            "complete_primary_output_review_cases": 30,
            "complete_double_output_review_cases": 10,
            "primary_task_precision": 0.95,
            "invalid_or_nonhuman_records_ignored": 0,
        },
        "adjudication_status": {
            "complete": True,
            "complete_cases": 30,
            "invalid_or_nonhuman_records_ignored": 0,
        },
        "agreement": {
            "complete": True,
            "double_annotated_case_pairs": 10,
            "double_reviewed_output_pairs": 10,
        },
        "reference_status_label": "adjudicated_human_reference",
        "freeze_status": {
            "complete": True,
            "manifest_hashes_valid": True,
            "metadata_valid": True,
            "required_files_missing_from_manifest": [],
        },
        "extraction_micro_f1": 0.95,
        "critical_omission_recall": 0.99,
        "unsupported_assertion_rate": 0.01,
        "evidence_quote_coverage": 1.0,
        "decision_gate_safety": 1.0,
        "priority_ndcg": 0.95,
        "human_approval_integrity": 1.0,
    }


def _break_gate(inputs: dict, gate_name: str) -> None:
    if gate_name == "full_frozen_dataset":
        inputs["split"] = "holdout"
    elif gate_name == "human_interviews":
        inputs["interviews"]["complete"] = False
    elif gate_name == "reference_reviews":
        inputs["readiness"]["complete"] = False
    elif gate_name == "output_reviews":
        inputs["task_metrics"]["complete"] = False
    elif gate_name == "adjudications":
        inputs["adjudication_status"]["complete"] = False
    elif gate_name == "reviewer_agreement":
        inputs["agreement"]["complete"] = False
    elif gate_name == "adjudicated_reference":
        inputs["reference_status_label"] = "provisional_candidate_reference"
    elif gate_name == "privacy_controls":
        inputs["interviews"]["invalid_or_nonhuman_records_ignored"] = 1
    elif gate_name == "human_input_freeze":
        inputs["freeze_status"]["complete"] = False
    elif gate_name == "extraction_micro_f1":
        inputs["extraction_micro_f1"] = 0.8999
    elif gate_name == "critical_omission_recall":
        inputs["critical_omission_recall"] = 0.9799
    elif gate_name == "unsupported_assertion_rate":
        inputs["unsupported_assertion_rate"] = 0.0101
    elif gate_name == "evidence_quote_coverage":
        inputs["evidence_quote_coverage"] = 0.9999
    elif gate_name == "decision_gate_safety":
        inputs["decision_gate_safety"] = 0.9999
    elif gate_name == "priority_ndcg":
        inputs["priority_ndcg"] = 0.8999
    elif gate_name == "primary_task_precision":
        inputs["task_metrics"]["primary_task_precision"] = 0.8999
    elif gate_name == "human_approval_integrity":
        inputs["human_approval_integrity"] = 0.9999
    else:  # pragma: no cover - keeps the parameter list honest
        raise AssertionError(gate_name)


GATE_NAMES = tuple(build_validation_gates(**_passing_gate_inputs()))


def test_complete_gate_contract_has_no_implicit_failures():
    gates = build_validation_gates(**_passing_gate_inputs())
    assert all(item["passed"] for item in gates.values())
    assert all(item["failure_reason"] is None for item in gates.values())


@pytest.mark.parametrize("gate_name", GATE_NAMES)
def test_each_validation_gate_fails_independently(gate_name: str):
    inputs = deepcopy(_passing_gate_inputs())
    _break_gate(inputs, gate_name)
    gates = build_validation_gates(**inputs)
    assert gates[gate_name]["passed"] is False
    assert gates[gate_name]["failure_reason"]
    assert all(
        item["passed"] for name, item in gates.items() if name != gate_name
    )


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in records)
        + "\n",
        encoding="utf-8",
    )


async def _create_complete_fixture(root: Path) -> dict[str, Path]:
    """Create synthetic gate fixtures; these records are never agronomic evidence."""

    dataset_path = root / "cases.jsonl"
    dataset_path.write_text(CANDIDATE_DATASET.read_text(encoding="utf-8"), encoding="utf-8")
    cases = load_cases(dataset_path)
    provider = LocalExtractionProvider()
    annotations: list[dict] = []
    outputs: list[dict] = []
    adjudications: list[dict] = []
    alias = "system-fixture-only"

    for case in cases:
        draft, _ = await provider.extract(case["note"])
        observation = StructuredObservation(
            **draft.model_dump(),
            field_id=case["field"]["id"],
            raw_text=case["note"],
            provider="local",
        )
        field = FieldRecord.model_validate(case["field"])
        _, missing, _, _, _, tasks = evaluate_policy(field, observation)
        reference_fields = {}
        for name in REFERENCE_FIELDS:
            value = getattr(observation, name)
            quote = observation.evidence_quotes.get(name)
            if value is None or value == "unknown":
                quote = None
            else:
                assert quote and quote in case["note"]
            reference_fields[name] = {
                "value": value,
                "evidence_quote": quote,
                "conflict": False,
            }

        case_annotations: list[dict] = []
        assignments = [("primary", "fixture-r01")]
        if case["double_review_required"]:
            assignments.append(("secondary", "fixture-r02"))
        for assignment, reviewer_id in assignments:
            annotation = {
                "schema_version": SCHEMA_VERSION,
                "test_fixture_only": True,
                "case_id": case["id"],
                "packet_id": reference_packet_id(case["id"]),
                "review_id": f"fixture-reference-{case['id']}-{assignment}",
                "reviewer_id": reviewer_id,
                "review_origin": "human",
                "review_assignment": assignment,
                "reviewer_role": "agronomist-fixture",
                "experience_band": "5-9",
                "consent_to_anonymous_results": True,
                "blind": True,
                "possible_prior_exposure": False,
                "completed_at": "2026-09-01",
                "reference_fields": reference_fields,
                "expected_missing": list(missing),
                "priority_relevance": case["priority_relevance"],
                "ranking_group": case["ranking_group"],
                "privacy_check": "passed",
            }
            annotations.append(annotation)
            case_annotations.append(annotation)
            outputs.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "test_fixture_only": True,
                    "case_id": case["id"],
                    "packet_id": output_packet_id(case["id"], alias),
                    "reference_packet_id": reference_packet_id(case["id"]),
                    "reference_lock_sha256": record_sha256(annotation),
                    "system_alias": alias,
                    "review_id": f"fixture-output-{case['id']}-{assignment}",
                    "reviewer_id": reviewer_id,
                    "review_origin": "human",
                    "review_assignment": assignment,
                    "consent_to_anonymous_results": True,
                    "blind": True,
                    "possible_prior_exposure": False,
                    "completed_at": "2026-09-01",
                    "privacy_check": "passed",
                    "fact_support": "all_supported",
                    "missing_critical_assessment": "correct",
                    "priority_assessment": "justified",
                    "task_labels": [
                        {
                            "task_index": index,
                            "classification": "appropriate",
                            "rationale": "Etiqueta sintética para probar el gate, no evidencia humana.",
                        }
                        for index in range(len(tasks))
                    ],
                    "would_reduce_followup_messages": "yes",
                    "would_reduce_return_visits": "uncertain",
                    "errors": [],
                    "overall_safety": "safe",
                }
            )

        adjudications.append(
            {
                "schema_version": SCHEMA_VERSION,
                "test_fixture_only": True,
                "adjudication_id": f"fixture-adjudication-{case['id']}",
                "case_id": case["id"],
                "status": "adjudicated",
                "adjudicator_id": "fixture-a01",
                "adjudication_origin": "human",
                "consent_to_anonymous_results": True,
                "source_review_ids": [item["review_id"] for item in case_annotations],
                "completed_at": "2026-09-01",
                "privacy_check": "passed",
                "final_reference_fields": reference_fields,
                "expected_missing": list(missing),
                "priority_relevance": case["priority_relevance"],
                "decisions": [
                    {
                        "target": "full-reference",
                        "decision": "accept-fixture-reference",
                        "rationale": "Solo prueba integración del gate; no representa juicio agronómico.",
                    }
                ],
            }
        )

    interviews = [
        {
            "schema_version": SCHEMA_VERSION,
            "test_fixture_only": True,
            "interview_origin": "human",
            "participant_id": f"fixture-p0{index}",
            "role": role,
            "experience_band": "5-9",
            "consent_aggregated_insights": True,
            "consent_sanitized_scenario": True,
            "recording_authorized": False,
            "privacy_review_status": "passed",
            "privacy_reviewer_id": "fixture-pr01",
            "completed_at": "2026-09-01",
            "hypothesis_assessment": "mixed",
            "workflow_summary": "Resumen sintético de prueba sin persona real.",
            "missing_information_summary": "Resumen sintético de prueba.",
            "counterevidence_summary": "Evidencia contraria sintética de prueba.",
        }
        for index, role in enumerate(("adviser", "producer", "scout"), start=1)
    ]

    paths = {
        "dataset": dataset_path,
        "interviews": root / "interviews.jsonl",
        "annotations": root / "annotations.jsonl",
        "outputs": root / "outputs.jsonl",
        "adjudications": root / "adjudications.jsonl",
        "manifest": root / "human-freeze.json",
    }
    _write_jsonl(paths["interviews"], interviews)
    _write_jsonl(paths["annotations"], annotations)
    _write_jsonl(paths["outputs"], outputs)
    _write_jsonl(paths["adjudications"], adjudications)
    files = [
        paths["dataset"],
        paths["interviews"],
        paths["annotations"],
        paths["outputs"],
        paths["adjudications"],
    ]
    manifest = {
        "manifest_version": "test-fixture-only",
        "freeze_scope": "human_reviewed_benchmark_inputs",
        "status": {
            "human_inputs_frozen": True,
            "candidate_only": False,
            "privacy_review_status": "passed",
            "holdout_policy": "not_used_for_tuning",
            "test_fixture_only": True,
            "evidence_claim_allowed": False,
        },
        "files": [
            {
                "path": item.relative_to(root).as_posix(),
                "canonical_sha256": canonical_sha256(item),
            }
            for item in files
        ],
    }
    paths["manifest"].write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return paths


def test_full_positive_fixture_proves_require_validated_contract(tmp_path: Path):
    paths = asyncio.run(_create_complete_fixture(tmp_path))
    result = asyncio.run(
        run(
            paths["dataset"],
            case_annotations_path=paths["annotations"],
            output_reviews_path=paths["outputs"],
            adjudications_path=paths["adjudications"],
            interview_records_path=paths["interviews"],
            human_freeze_manifest_path=paths["manifest"],
            freeze_root=tmp_path,
        )
    )
    assert result["benchmark_validated"] is True
    assert all(item["passed"] for item in result["validation_gates"].values())
    assert result["human_review_readiness"]["primary_reviewed_cases"] == 30
    assert result["human_review_readiness"]["double_reviewed_cases"] == 10
    assert result["task_review"]["complete_double_output_review_cases"] == 10
    assert result["task_precision"] == 1.0
    assert result["human_freeze_readiness"]["manifest_hashes_valid"] is True


def test_require_validated_exits_two_if_one_secondary_output_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
):
    paths = asyncio.run(_create_complete_fixture(tmp_path))
    reviews = [
        json.loads(line)
        for line in paths["outputs"].read_text(encoding="utf-8").splitlines()
    ]
    removed_case_id = next(
        item["case_id"] for item in reviews if item["review_assignment"] == "secondary"
    )
    reviews = [
        item
        for item in reviews
        if not (
            item["case_id"] == removed_case_id
            and item["review_assignment"] == "secondary"
        )
    ]
    _write_jsonl(paths["outputs"], reviews)
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    for item in manifest["files"]:
        if item["path"] == paths["outputs"].relative_to(tmp_path).as_posix():
            item["canonical_sha256"] = canonical_sha256(paths["outputs"])
    paths["manifest"].write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "agrofield-evaluate",
            str(paths["dataset"]),
            "--case-annotations",
            str(paths["annotations"]),
            "--output-reviews",
            str(paths["outputs"]),
            "--adjudications",
            str(paths["adjudications"]),
            "--interviews",
            str(paths["interviews"]),
            "--human-freeze-manifest",
            str(paths["manifest"]),
            "--freeze-root",
            str(tmp_path),
            "--require-validated",
        ],
    )
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
    report = json.loads(capsys.readouterr().out)
    assert report["task_review"]["missing_secondary_output_case_ids"] == [
        removed_case_id
    ]
    assert report["validation_gates"]["output_reviews"]["passed"] is False
