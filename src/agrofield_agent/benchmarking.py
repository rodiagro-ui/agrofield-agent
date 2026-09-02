from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from agrofield_agent.freeze import verify_manifest
from agrofield_agent.models import StructuredObservation, TaskProposal


REFERENCE_FIELDS = [
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

CATEGORICAL_FIELDS = ["crop_stage", "event_type", "access_safe"]
NUMERIC_FIELDS = [name for name in REFERENCE_FIELDS if name not in CATEGORICAL_FIELDS]
ERROR_CODES = [f"E{number}" for number in range(1, 9)]
TASK_CLASSIFICATIONS = {"appropriate", "premature", "unsafe", "not_assessable"}
REVIEW_ASSIGNMENTS = {"primary", "secondary"}
EXPERIENCE_BANDS = {"0-4", "5-9", "10-19", "20+"}
EVENT_TYPES = {"flooding", "hail", "wind", "mixed", "none", "unknown"}
FACT_SUPPORT_LABELS = {"all_supported", "some_unsupported", "not_assessable"}
MISSING_ASSESSMENT_LABELS = {"correct", "incomplete", "incorrect", "not_assessable"}
PRIORITY_ASSESSMENT_LABELS = {
    "justified",
    "partially_justified",
    "unjustified",
    "not_assessable",
}
SAFETY_LABELS = {"safe", "premature", "unsafe", "not_assessable"}
UTILITY_LABELS = {"yes", "no", "uncertain"}
ERROR_SEVERITIES = {"minor", "major", "critical"}
INTERVIEW_ROLES = {"adviser", "producer", "scout", "other"}
HYPOTHESIS_ASSESSMENTS = {"supports", "mixed", "refutes"}
SCHEMA_VERSION = "1.1.0-candidate"
_PLACEHOLDER_IDS = {
    "bfv1-000",
    "p00",
    "r00",
    "a00",
    "pr00",
    "review-random-id",
    "packet-random-id",
    "system-random-alias",
    "system-unlabeled",
    "adjudication-random-id",
}
_PROHIBITED_INTERVIEW_KEYS = {
    "name",
    "full_name",
    "initials",
    "email",
    "phone",
    "whatsapp",
    "employer",
    "company",
    "farm",
    "establishment",
    "coordinates",
    "latitude",
    "longitude",
}


def load_records(path: Path | None) -> list[dict[str, Any]]:
    """Load JSON or JSONL records from one file or a directory.

    Directories are deliberately non-recursive so templates elsewhere in the
    benchmark tree cannot be mistaken for completed reviews.
    """

    if path is None:
        return []
    if not path.exists():
        raise FileNotFoundError(path)
    paths = (
        sorted([*path.glob("*.jsonl"), *path.glob("*.json")])
        if path.is_dir()
        else [path]
    )
    records: list[dict[str, Any]] = []
    for item in paths:
        text = item.read_text(encoding="utf-8").strip()
        if not text:
            continue
        if item.suffix == ".jsonl":
            parsed = [
                json.loads(line)
                for line in text.splitlines()
                if line.strip()
            ]
        else:
            body = json.loads(text)
            parsed = body if isinstance(body, list) else [body]
        for record in parsed:
            if not isinstance(record, dict):
                raise ValueError(f"Expected object record in {item}")
            records.append(record)
    return records


def load_cases(path: Path, split: str | None = None) -> list[dict[str, Any]]:
    cases = load_records(path)
    if split and split != "all":
        cases = [case for case in cases if case.get("split") == split]
    ids = [case.get("id") for case in cases]
    if any(not case_id for case_id in ids):
        raise ValueError("Every benchmark case must have a non-empty id")
    if len(set(ids)) != len(ids):
        raise ValueError("Benchmark case IDs must be unique")
    return cases


def _field_values(record: dict[str, Any], key: str) -> dict[str, Any]:
    raw = record.get(key, {})
    values: dict[str, Any] = {}
    for name in REFERENCE_FIELDS:
        item = raw.get(name)
        values[name] = item.get("value") if isinstance(item, dict) else item
    return values


def _valid_identifier(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.strip().lower()
    return (
        normalized not in _PLACEHOLDER_IDS
        and "random" not in normalized
        and "yyyy" not in normalized
        and "__" not in normalized
    )


def _valid_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _valid_reference_value(name: str, value: Any) -> bool:
    if value is None:
        return True
    if name == "event_type":
        return value in EVENT_TYPES
    if name == "access_safe":
        return isinstance(value, bool)
    if name == "crop_stage":
        return isinstance(value, str) and bool(value.strip()) and value != "unknown"
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if not math.isfinite(float(value)) or value < 0:
        return False
    if name == "sample_points" and not isinstance(value, int):
        return False
    if name in {
        "affected_area_pct",
        "standing_water_pct",
        "lodging_pct",
        "stem_damage_pct",
    } and value > 100:
        return False
    return True


def _valid_reference_fields(record: dict[str, Any], key: str) -> bool:
    fields = record.get(key)
    if not isinstance(fields, dict) or set(fields) != set(REFERENCE_FIELDS):
        return False
    supported_values = 0
    for name in REFERENCE_FIELDS:
        item = fields.get(name)
        if not isinstance(item, dict):
            return False
        if not {"value", "evidence_quote", "conflict"} <= set(item):
            return False
        value = item.get("value")
        quote = item.get("evidence_quote")
        if not _valid_reference_value(name, value):
            return False
        if quote is not None and (not isinstance(quote, str) or not quote.strip()):
            return False
        if value is not None and value != "unknown" and not (
            isinstance(quote, str) and quote.strip()
        ):
            return False
        supported_values += int(value is not None and value != "unknown")
        if not isinstance(item.get("conflict"), bool):
            return False
    return supported_values > 0


def _valid_expected_missing(value: Any) -> bool:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item in REFERENCE_FIELDS for item in value
    ):
        return False
    return len(value) == len(set(value))


def _valid_priority(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 4


def _valid_task_label(item: Any) -> bool:
    return (
        isinstance(item, dict)
        and isinstance(item.get("task_index"), int)
        and not isinstance(item.get("task_index"), bool)
        and item["task_index"] >= 0
        and item.get("classification") in TASK_CLASSIFICATIONS
        and isinstance(item.get("rationale"), str)
        and bool(item["rationale"].strip())
    )


def _valid_error(item: Any) -> bool:
    return (
        isinstance(item, dict)
        and item.get("code") in ERROR_CODES
        and item.get("severity") in ERROR_SEVERITIES
        and isinstance(item.get("target"), str)
        and bool(item["target"].strip())
        and isinstance(item.get("rationale"), str)
        and bool(item["rationale"].strip())
    )


def _complete_task_labels(review: dict[str, Any], task_count: int) -> bool:
    labels = review.get("task_labels")
    if not isinstance(labels, list) or not all(_valid_task_label(item) for item in labels):
        return False
    indices = [item["task_index"] for item in labels]
    return len(indices) == task_count and set(indices) == set(range(task_count))


def record_sha256(record: dict[str, Any]) -> str:
    """Hash one locked JSON record using a deterministic representation."""

    payload = json.dumps(
        record, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _valid_human_annotation(record: dict[str, Any]) -> bool:
    return (
        record.get("schema_version") == SCHEMA_VERSION
        and record.get("review_origin") == "human"
        and record.get("blind") is True
        and record.get("consent_to_anonymous_results") is True
        and record.get("review_assignment") in REVIEW_ASSIGNMENTS
        and _valid_identifier(record.get("review_id"))
        and _valid_identifier(record.get("reviewer_id"))
        and _valid_identifier(record.get("case_id"))
        and record.get("packet_id") == reference_packet_id(record["case_id"])
        and isinstance(record.get("reviewer_role"), str)
        and bool(record["reviewer_role"].strip())
        and record.get("experience_band") in EXPERIENCE_BANDS
        and isinstance(record.get("possible_prior_exposure"), bool)
        and _valid_iso_date(record.get("completed_at"))
        and record.get("privacy_check") == "passed"
        and _valid_reference_fields(record, "reference_fields")
        and _valid_expected_missing(record.get("expected_missing"))
        and _valid_priority(record.get("priority_relevance"))
        and _valid_identifier(record.get("ranking_group"))
    )


def _valid_human_output_review(record: dict[str, Any]) -> bool:
    task_labels = record.get("task_labels")
    errors = record.get("errors")
    return (
        record.get("schema_version") == SCHEMA_VERSION
        and record.get("review_origin") == "human"
        and record.get("blind") is True
        and record.get("consent_to_anonymous_results") is True
        and record.get("review_assignment") in REVIEW_ASSIGNMENTS
        and _valid_identifier(record.get("review_id"))
        and _valid_identifier(record.get("reviewer_id"))
        and _valid_identifier(record.get("case_id"))
        and _valid_identifier(record.get("system_alias"))
        and record.get("packet_id")
        == output_packet_id(record["case_id"], record["system_alias"])
        and record.get("reference_packet_id") == reference_packet_id(record["case_id"])
        and isinstance(record.get("reference_lock_sha256"), str)
        and bool(re.fullmatch(r"[0-9a-f]{64}", record["reference_lock_sha256"]))
        and isinstance(record.get("possible_prior_exposure"), bool)
        and _valid_iso_date(record.get("completed_at"))
        and record.get("privacy_check") == "passed"
        and record.get("fact_support") in FACT_SUPPORT_LABELS
        and record.get("missing_critical_assessment") in MISSING_ASSESSMENT_LABELS
        and record.get("priority_assessment") in PRIORITY_ASSESSMENT_LABELS
        and record.get("overall_safety") in SAFETY_LABELS
        and record.get("would_reduce_followup_messages") in UTILITY_LABELS
        and record.get("would_reduce_return_visits") in UTILITY_LABELS
        and isinstance(task_labels, list)
        and all(_valid_task_label(item) for item in task_labels)
        and len({item["task_index"] for item in task_labels}) == len(task_labels)
        and isinstance(errors, list)
        and all(_valid_error(item) for item in errors)
    )


def _valid_human_adjudication(
    record: dict[str, Any], *, double_review_required: bool
) -> bool:
    required_sources = 2 if double_review_required else 1
    sources = record.get("source_review_ids")
    decisions = record.get("decisions")
    return (
        record.get("schema_version") == SCHEMA_VERSION
        and record.get("status") == "adjudicated"
        and record.get("adjudication_origin") == "human"
        and record.get("consent_to_anonymous_results") is True
        and _valid_identifier(record.get("adjudication_id"))
        and _valid_identifier(record.get("case_id"))
        and _valid_identifier(record.get("adjudicator_id"))
        and _valid_iso_date(record.get("completed_at"))
        and record.get("privacy_check") == "passed"
        and isinstance(sources, list)
        and len(set(sources)) >= required_sources
        and all(_valid_identifier(item) for item in sources)
        and _valid_reference_fields(record, "final_reference_fields")
        and _valid_expected_missing(record.get("expected_missing"))
        and _valid_priority(record.get("priority_relevance"))
        and isinstance(decisions, list)
        and bool(decisions)
        and all(
            isinstance(item, dict)
            and _valid_identifier(item.get("target"))
            and _valid_identifier(item.get("decision"))
            and isinstance(item.get("rationale"), str)
            and bool(item["rationale"].strip())
            for item in decisions
        )
    )


def _valid_human_interview(record: dict[str, Any]) -> bool:
    if _PROHIBITED_INTERVIEW_KEYS & set(record):
        return False
    return (
        record.get("schema_version") == SCHEMA_VERSION
        and record.get("interview_origin") == "human"
        and _valid_identifier(record.get("participant_id"))
        and record.get("role") in INTERVIEW_ROLES
        and record.get("experience_band") in EXPERIENCE_BANDS
        and record.get("consent_aggregated_insights") is True
        and record.get("consent_sanitized_scenario") is True
        and record.get("recording_authorized") is False
        and record.get("privacy_review_status") == "passed"
        and _valid_identifier(record.get("privacy_reviewer_id"))
        and _valid_iso_date(record.get("completed_at"))
        and record.get("hypothesis_assessment") in HYPOTHESIS_ASSESSMENTS
        and all(
            isinstance(record.get(name), str) and bool(record[name].strip())
            for name in (
                "workflow_summary",
                "missing_information_summary",
                "counterevidence_summary",
            )
        )
    )


def human_case_annotations(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if _valid_human_annotation(record)]


def human_output_reviews(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if _valid_human_output_review(record)]


def human_interviews(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if _valid_human_interview(record)]


def reference_for_case(
    case: dict[str, Any],
    annotations: list[dict[str, Any]],
    adjudications: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[str], float | None, str]:
    case_id = case["id"]
    valid_annotations = [
        item
        for item in human_case_annotations(annotations)
        if item.get("case_id") == case_id
    ]
    primary = [
        item for item in valid_annotations if item.get("review_assignment") == "primary"
    ]
    secondary = [
        item
        for item in valid_annotations
        if item.get("review_assignment") == "secondary"
    ]
    expected_source_ids = {primary[0]["review_id"]} if len(primary) == 1 else set()
    if case.get("double_review_required"):
        if len(secondary) == 1:
            expected_source_ids.add(secondary[0]["review_id"])
        else:
            expected_source_ids = set()
    adjudicated = [
        item
        for item in adjudications
        if item.get("case_id") == case_id
        and _valid_human_adjudication(
            item, double_review_required=bool(case.get("double_review_required"))
        )
        and expected_source_ids
        and set(item.get("source_review_ids", [])) == expected_source_ids
    ]
    if adjudicated:
        item = sorted(adjudicated, key=lambda value: value.get("adjudication_id", ""))[-1]
        return (
            _field_values(item, "final_reference_fields"),
            list(item.get("expected_missing", [])),
            item.get("priority_relevance"),
            "adjudicated_human_reference",
        )

    reviewed = sorted(
        primary,
        key=lambda value: (value.get("reviewer_id", ""), value.get("review_id", "")),
    )
    if reviewed:
        item = reviewed[0]
        return (
            _field_values(item, "reference_fields"),
            list(item.get("expected_missing", [])),
            item.get("priority_relevance"),
            "primary_human_preliminary",
        )

    if "candidate_reference" in case:
        candidate = case["candidate_reference"]
        return (
            {name: candidate.get("fields", {}).get(name) for name in REFERENCE_FIELDS},
            list(candidate.get("expected_missing", [])),
            case.get("priority_relevance"),
            "provisional_candidate_reference",
        )

    return (
        {name: case.get("gold", {}).get(name) for name in REFERENCE_FIELDS},
        list(case.get("expected_missing", [])),
        case.get("priority_relevance"),
        "synthetic_local_fixture_reference",
    )


def reference_status(sources: Iterable[str]) -> tuple[str, dict[str, int]]:
    counts = dict(sorted(Counter(sources).items()))
    if counts and set(counts) == {"adjudicated_human_reference"}:
        status = "adjudicated_human_reference"
    elif any("human" in source for source in counts):
        status = "mixed_or_preliminary_human_reference"
    elif counts and set(counts) == {"synthetic_local_fixture_reference"}:
        status = "synthetic_local_fixture_reference"
    else:
        status = "provisional_candidate_reference"
    return status, counts


def cohens_kappa(labels_a: list[str], labels_b: list[str]) -> float | None:
    if len(labels_a) != len(labels_b):
        raise ValueError("Cohen's kappa requires paired label lists of equal length")
    if not labels_a:
        return None
    total = len(labels_a)
    observed = sum(a == b for a, b in zip(labels_a, labels_b, strict=True)) / total
    counts_a = Counter(labels_a)
    counts_b = Counter(labels_b)
    categories = set(counts_a) | set(counts_b)
    expected = sum(
        (counts_a[label] / total) * (counts_b[label] / total)
        for label in categories
    )
    if math.isclose(expected, 1.0):
        return 1.0 if math.isclose(observed, 1.0) else 0.0
    return (observed - expected) / (1 - expected)


def _metric(labels_a: list[str], labels_b: list[str]) -> dict[str, Any]:
    if not labels_a:
        return {
            "paired_items": 0,
            "raw_agreement": None,
            "raw_disagreement": None,
            "cohens_kappa": None,
        }
    agreements = sum(a == b for a, b in zip(labels_a, labels_b, strict=True))
    total = len(labels_a)
    kappa = cohens_kappa(labels_a, labels_b)
    return {
        "paired_items": total,
        "raw_agreement": round(agreements / total, 4),
        "raw_disagreement": round(1 - agreements / total, 4),
        "cohens_kappa": round(kappa, 4) if kappa is not None else None,
    }


def _assigned_pair(
    records: list[dict[str, Any]], case_id: str
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    primary = [
        item
        for item in records
        if item.get("case_id") == case_id
        and item.get("review_assignment") == "primary"
    ]
    secondary = [
        item
        for item in records
        if item.get("case_id") == case_id
        and item.get("review_assignment") == "secondary"
    ]
    if len(primary) != 1 or len(secondary) != 1:
        return None
    if primary[0]["reviewer_id"] == secondary[0]["reviewer_id"]:
        return None
    return primary[0], secondary[0]


def _reference_agreement_metrics(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, Any]:
    missing_a: list[str] = []
    missing_b: list[str] = []
    categorical: dict[str, tuple[list[str], list[str]]] = {
        name: ([], []) for name in CATEGORICAL_FIELDS
    }
    numeric_equal = numeric_total = 0
    for first, second in pairs:
        values_a = _field_values(first, "reference_fields")
        values_b = _field_values(second, "reference_fields")
        expected_a = set(first.get("expected_missing", []))
        expected_b = set(second.get("expected_missing", []))
        for name in REFERENCE_FIELDS:
            missing_a.append("missing" if name in expected_a else "not_missing")
            missing_b.append("missing" if name in expected_b else "not_missing")
        for name in CATEGORICAL_FIELDS:
            categorical[name][0].append(json.dumps(values_a[name], sort_keys=True))
            categorical[name][1].append(json.dumps(values_b[name], sort_keys=True))
        for name in NUMERIC_FIELDS:
            value_a, value_b = values_a[name], values_b[name]
            numeric_total += 1
            if value_a is None and value_b is None:
                numeric_equal += 1
            elif isinstance(value_a, (int, float)) and isinstance(
                value_b, (int, float)
            ):
                numeric_equal += int(
                    math.isclose(float(value_a), float(value_b), abs_tol=0.01)
                )

    nominal_pairs = len(missing_a) + sum(
        len(values[0]) for values in categorical.values()
    )
    nominal_disagreements = sum(
        a != b for a, b in zip(missing_a, missing_b, strict=True)
    )
    nominal_disagreements += sum(
        sum(a != b for a, b in zip(values[0], values[1], strict=True))
        for values in categorical.values()
    )
    return {
        "raw_disagreement": (
            round(nominal_disagreements / nominal_pairs, 4)
            if nominal_pairs
            else None
        ),
        "missing_critical": _metric(missing_a, missing_b),
        "categorical_fields": {
            name: _metric(values[0], values[1])
            for name, values in categorical.items()
        },
        "numeric_fields": {
            "paired_items": numeric_total,
            "raw_agreement": (
                round(numeric_equal / numeric_total, 4) if numeric_total else None
            ),
            "raw_disagreement": (
                round(1 - numeric_equal / numeric_total, 4)
                if numeric_total
                else None
            ),
            "cohens_kappa": None,
        },
    }


def _output_agreement_metrics(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, Any]:
    output_fields = [
        "fact_support",
        "missing_critical_assessment",
        "priority_assessment",
        "overall_safety",
    ]
    output_labels: dict[str, tuple[list[str], list[str]]] = {
        name: ([], []) for name in output_fields
    }
    task_a: list[str] = []
    task_b: list[str] = []
    for first, second in pairs:
        for name in output_fields:
            output_labels[name][0].append(str(first.get(name)))
            output_labels[name][1].append(str(second.get(name)))
        tasks_a = {
            item.get("task_index"): item.get("classification")
            for item in first.get("task_labels", [])
        }
        tasks_b = {
            item.get("task_index"): item.get("classification")
            for item in second.get("task_labels", [])
        }
        for task_index in sorted(set(tasks_a) & set(tasks_b), key=str):
            task_a.append(str(tasks_a[task_index]))
            task_b.append(str(tasks_b[task_index]))

    return {
        "output_judgements": {
            name: _metric(values[0], values[1])
            for name, values in output_labels.items()
        },
        "task_classification": _metric(task_a, task_b),
    }


def _pair_has_possible_prior_exposure(
    pair: tuple[dict[str, Any], dict[str, Any]],
) -> bool:
    return any(item.get("possible_prior_exposure") is True for item in pair)


def reviewer_agreement(
    cases: list[dict[str, Any]],
    case_annotation_records: list[dict[str, Any]],
    output_review_records: list[dict[str, Any]],
    expected_tasks_by_case: dict[str, int] | None = None,
) -> dict[str, Any]:
    annotations = human_case_annotations(case_annotation_records)
    outputs = human_output_reviews(output_review_records)
    required_case_ids = [
        case["id"] for case in cases if case.get("double_review_required")
    ]
    annotation_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    missing_annotation_pairs: list[str] = []
    for case_id in required_case_ids:
        pair = _assigned_pair(annotations, case_id)
        if pair is None:
            missing_annotation_pairs.append(case_id)
        else:
            annotation_pairs.append(pair)

    output_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    missing_output_pairs: list[str] = []
    expected = expected_tasks_by_case or {}
    for case_id in required_case_ids:
        pair = _assigned_pair(outputs, case_id)
        task_count = expected.get(case_id)
        if (
            pair is None
            or pair[0].get("packet_id") != pair[1].get("packet_id")
            or pair[0].get("system_alias") != pair[1].get("system_alias")
            or task_count is None
            or not _complete_task_labels(pair[0], task_count)
            or not _complete_task_labels(pair[1], task_count)
        ):
            missing_output_pairs.append(case_id)
        else:
            output_pairs.append(pair)
    reference_metrics = _reference_agreement_metrics(annotation_pairs)
    output_metrics = _output_agreement_metrics(output_pairs)
    unexposed_annotation_pairs = [
        pair
        for pair in annotation_pairs
        if not _pair_has_possible_prior_exposure(pair)
    ]
    unexposed_output_pairs = [
        pair for pair in output_pairs if not _pair_has_possible_prior_exposure(pair)
    ]
    exposed_reference_case_ids = sorted(
        pair[0]["case_id"]
        for pair in annotation_pairs
        if _pair_has_possible_prior_exposure(pair)
    )
    exposed_output_case_ids = sorted(
        pair[0]["case_id"]
        for pair in output_pairs
        if _pair_has_possible_prior_exposure(pair)
    )
    complete = (
        bool(required_case_ids)
        and len(annotation_pairs) == len(required_case_ids)
        and len(output_pairs) == len(required_case_ids)
    )
    return {
        "status": (
            "complete"
            if complete
            else "partial"
            if annotation_pairs or output_pairs
            else "pending_human_double_review"
        ),
        "required_double_review_cases": len(required_case_ids),
        "double_annotated_case_pairs": len(annotation_pairs),
        "double_reviewed_output_pairs": len(output_pairs),
        "missing_reference_pair_case_ids": missing_annotation_pairs,
        "missing_output_pair_case_ids": missing_output_pairs,
        "complete": complete,
        **reference_metrics,
        **output_metrics,
        "exposure_sensitivity": {
            "binding_metrics_include_all_complete_pairs": True,
            "reference": {
                "all_pair_count": len(annotation_pairs),
                "all_pair_case_ids": sorted(
                    pair[0]["case_id"] for pair in annotation_pairs
                ),
                "without_possible_prior_exposure_pair_count": len(
                    unexposed_annotation_pairs
                ),
                "excluded_possible_prior_exposure_case_ids": (
                    exposed_reference_case_ids
                ),
                "all_pair_metrics": reference_metrics,
                "without_possible_prior_exposure_metrics": (
                    _reference_agreement_metrics(unexposed_annotation_pairs)
                ),
            },
            "output": {
                "all_pair_count": len(output_pairs),
                "all_pair_case_ids": sorted(
                    pair[0]["case_id"] for pair in output_pairs
                ),
                "without_possible_prior_exposure_pair_count": len(
                    unexposed_output_pairs
                ),
                "excluded_possible_prior_exposure_case_ids": exposed_output_case_ids,
                "all_pair_metrics": output_metrics,
                "without_possible_prior_exposure_metrics": (
                    _output_agreement_metrics(unexposed_output_pairs)
                ),
            },
        },
    }


def review_readiness(
    cases: list[dict[str, Any]], annotation_records: list[dict[str, Any]]
) -> dict[str, Any]:
    annotations = human_case_annotations(annotation_records)
    case_ids = {case["id"] for case in cases}
    relevant_annotations = [
        item for item in annotations if item.get("case_id") in case_ids
    ]
    primary_reviewer_ids = sorted(
        {
            item["reviewer_id"]
            for item in relevant_annotations
            if item.get("review_assignment") == "primary"
        }
    )
    secondary_reviewer_ids = sorted(
        {
            item["reviewer_id"]
            for item in relevant_annotations
            if item.get("review_assignment") == "secondary"
        }
    )
    reviewer_assignment_overlap_ids = sorted(
        set(primary_reviewer_ids) & set(secondary_reviewer_ids)
    )
    required_double_ids = {
        case["id"] for case in cases if case.get("double_review_required")
    }
    primary_ids: list[str] = []
    secondary_ids: list[str] = []
    missing_primary: list[str] = []
    missing_secondary: list[str] = []
    duplicate_primary: list[str] = []
    duplicate_secondary: list[str] = []
    independence_failures: list[str] = []
    unexpected_secondary: list[str] = []
    evidence_failures: list[str] = []
    context_failures: list[str] = []

    for case in cases:
        case_id = case["id"]
        primary = [
            item
            for item in annotations
            if item.get("case_id") == case_id
            and item.get("review_assignment") == "primary"
        ]
        secondary = [
            item
            for item in annotations
            if item.get("case_id") == case_id
            and item.get("review_assignment") == "secondary"
        ]
        if len(primary) == 1:
            primary_ids.append(case_id)
        else:
            missing_primary.append(case_id)
            if len(primary) > 1:
                duplicate_primary.append(case_id)
        if case_id in required_double_ids:
            if len(secondary) == 1:
                secondary_ids.append(case_id)
            else:
                missing_secondary.append(case_id)
                if len(secondary) > 1:
                    duplicate_secondary.append(case_id)
            if (
                len(primary) == 1
                and len(secondary) == 1
                and primary[0]["reviewer_id"] == secondary[0]["reviewer_id"]
            ):
                independence_failures.append(case_id)
        elif secondary:
            unexpected_secondary.append(case_id)

        for annotation in [*primary, *secondary]:
            if annotation.get("ranking_group") != (
                case.get("ranking_group") or case.get("scenario")
            ):
                context_failures.append(case_id)
            if any(
                item.get("value") is not None
                and item.get("value") != "unknown"
                and item.get("evidence_quote") not in case["note"]
                for item in annotation["reference_fields"].values()
            ):
                evidence_failures.append(case_id)

    unknown_case_ids = sorted(
        {item["case_id"] for item in annotations if item["case_id"] not in case_ids}
    )
    review_ids = [item["review_id"] for item in annotations]
    duplicate_review_ids = sorted(
        review_id for review_id, count in Counter(review_ids).items() if count > 1
    )
    invalid_count = len(annotation_records) - len(annotations)
    complete = (
        bool(cases)
        and len(primary_ids) == len(cases)
        and len(secondary_ids) == len(required_double_ids)
        and not duplicate_primary
        and not duplicate_secondary
        and not independence_failures
        and not unexpected_secondary
        and not evidence_failures
        and not context_failures
        and not unknown_case_ids
        and not duplicate_review_ids
        and not reviewer_assignment_overlap_ids
        and invalid_count == 0
    )
    return {
        "required_primary_cases": len(cases),
        "primary_reviewed_cases": len(primary_ids),
        "missing_primary_case_ids": missing_primary,
        "duplicate_primary_case_ids": duplicate_primary,
        "required_double_review_cases": len(required_double_ids),
        "double_reviewed_cases": len(secondary_ids),
        "missing_secondary_case_ids": missing_secondary,
        "duplicate_secondary_case_ids": duplicate_secondary,
        "reviewer_independence_failure_case_ids": independence_failures,
        "primary_reviewer_ids": primary_reviewer_ids,
        "secondary_reviewer_ids": secondary_reviewer_ids,
        "reviewer_assignment_overlap_ids": reviewer_assignment_overlap_ids,
        "reviewer_role_independence_complete": (
            not independence_failures and not reviewer_assignment_overlap_ids
        ),
        "unexpected_secondary_case_ids": unexpected_secondary,
        "evidence_quote_failure_case_ids": sorted(set(evidence_failures)),
        "context_mismatch_case_ids": sorted(set(context_failures)),
        "unknown_case_ids": unknown_case_ids,
        "duplicate_review_ids": duplicate_review_ids,
        "valid_human_records": len(annotations),
        "invalid_or_nonhuman_records_ignored": invalid_count,
        "complete": complete,
    }


def task_review_metrics(
    cases: list[dict[str, Any]],
    output_review_records: list[dict[str, Any]],
    expected_tasks_by_case: dict[str, int],
    case_annotation_records: list[dict[str, Any]],
) -> dict[str, Any]:
    reviews = human_output_reviews(output_review_records)
    annotations = human_case_annotations(case_annotation_records)
    case_ids = {case["id"] for case in cases}
    double_ids = {case["id"] for case in cases if case.get("double_review_required")}
    primary_counts: Counter[str] = Counter()
    secondary_counts: Counter[str] = Counter()
    complete_primary_ids: list[str] = []
    complete_secondary_ids: list[str] = []
    missing_primary_ids: list[str] = []
    missing_secondary_ids: list[str] = []
    duplicate_primary_ids: list[str] = []
    duplicate_secondary_ids: list[str] = []
    pair_mismatch_ids: list[str] = []
    lock_failure_ids: list[str] = []
    unexpected_secondary_ids: list[str] = []

    annotation_locks = {
        (item["case_id"], item["review_assignment"], item["reviewer_id"]): record_sha256(item)
        for item in annotations
    }

    def locked_and_complete(review: dict[str, Any], task_count: int) -> bool:
        expected_lock = annotation_locks.get(
            (review["case_id"], review["review_assignment"], review["reviewer_id"])
        )
        return (
            _complete_task_labels(review, task_count)
            and expected_lock is not None
            and review.get("reference_lock_sha256") == expected_lock
        )

    primary_by_case: dict[str, dict[str, Any]] = {}
    secondary_by_case: dict[str, dict[str, Any]] = {}
    for case in cases:
        case_id = case["id"]
        task_count = expected_tasks_by_case.get(case_id)
        if task_count is None:
            missing_primary_ids.append(case_id)
            if case_id in double_ids:
                missing_secondary_ids.append(case_id)
            continue
        primary = [
            item
            for item in reviews
            if item.get("case_id") == case_id
            and item.get("review_assignment") == "primary"
        ]
        secondary = [
            item
            for item in reviews
            if item.get("case_id") == case_id
            and item.get("review_assignment") == "secondary"
        ]
        if len(primary) == 1 and locked_and_complete(primary[0], task_count):
            primary_by_case[case_id] = primary[0]
            complete_primary_ids.append(case_id)
            primary_counts.update(item["classification"] for item in primary[0]["task_labels"])
        else:
            missing_primary_ids.append(case_id)
            if len(primary) > 1:
                duplicate_primary_ids.append(case_id)
            elif len(primary) == 1:
                lock_failure_ids.append(case_id)

        if case_id in double_ids:
            if len(secondary) == 1 and locked_and_complete(secondary[0], task_count):
                secondary_by_case[case_id] = secondary[0]
                complete_secondary_ids.append(case_id)
                secondary_counts.update(
                    item["classification"] for item in secondary[0]["task_labels"]
                )
            else:
                missing_secondary_ids.append(case_id)
                if len(secondary) > 1:
                    duplicate_secondary_ids.append(case_id)
                elif len(secondary) == 1:
                    lock_failure_ids.append(case_id)
        elif secondary:
            unexpected_secondary_ids.append(case_id)

    for case_id in sorted(double_ids & set(primary_by_case) & set(secondary_by_case)):
        primary = primary_by_case[case_id]
        secondary = secondary_by_case[case_id]
        if (
            primary["reviewer_id"] == secondary["reviewer_id"]
            or primary["packet_id"] != secondary["packet_id"]
            or primary["system_alias"] != secondary["system_alias"]
        ):
            pair_mismatch_ids.append(case_id)

    unknown_case_ids = sorted(
        {item["case_id"] for item in reviews if item["case_id"] not in case_ids}
    )
    review_ids = [item["review_id"] for item in reviews]
    duplicate_review_ids = sorted(
        review_id for review_id, count in Counter(review_ids).items() if count > 1
    )
    invalid_count = len(output_review_records) - len(reviews)
    primary_denominator = sum(primary_counts.values())
    secondary_denominator = sum(secondary_counts.values())
    primary_complete = (
        bool(cases)
        and len(complete_primary_ids) == len(cases)
        and not duplicate_primary_ids
    )
    double_complete = (
        bool(double_ids)
        and len(complete_secondary_ids) == len(double_ids)
        and not duplicate_secondary_ids
        and not pair_mismatch_ids
    )
    complete = (
        primary_complete
        and double_complete
        and not lock_failure_ids
        and not unexpected_secondary_ids
        and not unknown_case_ids
        and not duplicate_review_ids
        and invalid_count == 0
    )
    primary_precision = (
        round(primary_counts["appropriate"] / primary_denominator, 4)
        if primary_denominator
        else None
    )
    return {
        "task_precision": primary_precision,
        "binding_metric": "primary_task_precision",
        "primary_task_precision": primary_precision,
        "adjudicated_task_precision": None,
        "adjudicated_task_precision_status": "not_collected_binding_metric_is_primary",
        "primary_task_review_counts": {
            label: primary_counts[label] for label in sorted(TASK_CLASSIFICATIONS)
        },
        "secondary_task_review_counts": {
            label: secondary_counts[label] for label in sorted(TASK_CLASSIFICATIONS)
        },
        "primary_reviewed_task_labels": primary_denominator,
        "secondary_reviewed_task_labels": secondary_denominator,
        "required_primary_output_review_cases": len(cases),
        "complete_primary_output_review_cases": len(complete_primary_ids),
        "missing_primary_output_case_ids": sorted(set(missing_primary_ids)),
        "duplicate_primary_output_case_ids": sorted(set(duplicate_primary_ids)),
        "required_double_output_review_cases": len(double_ids),
        "complete_double_output_review_cases": len(complete_secondary_ids),
        "missing_secondary_output_case_ids": sorted(set(missing_secondary_ids)),
        "duplicate_secondary_output_case_ids": sorted(set(duplicate_secondary_ids)),
        "pair_mismatch_case_ids": pair_mismatch_ids,
        "phase_a_lock_failure_case_ids": sorted(set(lock_failure_ids)),
        "unexpected_secondary_output_case_ids": unexpected_secondary_ids,
        "unknown_case_ids": unknown_case_ids,
        "duplicate_review_ids": duplicate_review_ids,
        "valid_human_records": len(reviews),
        "invalid_or_nonhuman_records_ignored": invalid_count,
        "primary_complete": primary_complete,
        "double_complete": double_complete,
        "complete": complete,
        "status": "complete" if complete else "pending_or_incomplete_human_output_review",
    }


def interview_readiness(interview_records: list[dict[str, Any]]) -> dict[str, Any]:
    interviews = human_interviews(interview_records)
    participant_ids = [item["participant_id"] for item in interviews]
    duplicates = sorted(
        participant_id
        for participant_id, count in Counter(participant_ids).items()
        if count > 1
    )
    invalid_count = len(interview_records) - len(interviews)
    unique_count = len(set(participant_ids))
    complete = 3 <= unique_count <= 5 and not duplicates and invalid_count == 0
    return {
        "required_minimum": 3,
        "allowed_maximum": 5,
        "valid_unique_interviews": unique_count,
        "duplicate_participant_ids": duplicates,
        "roles": dict(sorted(Counter(item["role"] for item in interviews).items())),
        "experience_bands": dict(
            sorted(Counter(item["experience_band"] for item in interviews).items())
        ),
        "invalid_or_nonhuman_records_ignored": invalid_count,
        "complete": complete,
    }


def adjudication_readiness(
    cases: list[dict[str, Any]],
    annotation_records: list[dict[str, Any]],
    adjudication_records: list[dict[str, Any]],
) -> dict[str, Any]:
    annotations = human_case_annotations(annotation_records)
    case_by_id = {case["id"]: case for case in cases}
    valid: list[dict[str, Any]] = []
    for item in adjudication_records:
        case = case_by_id.get(item.get("case_id"))
        if case and _valid_human_adjudication(
            item, double_review_required=bool(case.get("double_review_required"))
        ):
            valid.append(item)

    complete_case_ids: list[str] = []
    missing_case_ids: list[str] = []
    duplicate_case_ids: list[str] = []
    source_mismatch_ids: list[str] = []
    adjudicator_overlap_ids: list[str] = []
    for case in cases:
        case_id = case["id"]
        items = [item for item in valid if item["case_id"] == case_id]
        if len(items) != 1:
            missing_case_ids.append(case_id)
            if len(items) > 1:
                duplicate_case_ids.append(case_id)
            continue
        primary = [
            item
            for item in annotations
            if item["case_id"] == case_id and item["review_assignment"] == "primary"
        ]
        secondary = [
            item
            for item in annotations
            if item["case_id"] == case_id and item["review_assignment"] == "secondary"
        ]
        expected_sources = (
            {primary[0]["review_id"]}
            if len(primary) == 1
            else set()
        )
        reviewers = {item["reviewer_id"] for item in primary}
        if case.get("double_review_required"):
            if len(secondary) == 1:
                expected_sources.add(secondary[0]["review_id"])
                reviewers.add(secondary[0]["reviewer_id"])
            else:
                expected_sources = set()
        adjudication = items[0]
        if set(adjudication["source_review_ids"]) != expected_sources or not expected_sources:
            source_mismatch_ids.append(case_id)
            continue
        if adjudication["adjudicator_id"] in reviewers:
            adjudicator_overlap_ids.append(case_id)
            continue
        complete_case_ids.append(case_id)

    ids = [item["adjudication_id"] for item in valid]
    duplicate_ids = sorted(item for item, count in Counter(ids).items() if count > 1)
    unknown_case_ids = sorted(
        {item["case_id"] for item in valid if item["case_id"] not in case_by_id}
    )
    invalid_count = len(adjudication_records) - len(valid)
    reviewer_ids = sorted(
        {
            item["reviewer_id"]
            for item in annotations
            if item.get("case_id") in case_by_id
        }
    )
    adjudicator_ids = sorted({item["adjudicator_id"] for item in valid})
    reviewer_adjudicator_overlap_ids = sorted(
        set(reviewer_ids) & set(adjudicator_ids)
    )
    complete = (
        bool(cases)
        and len(complete_case_ids) == len(cases)
        and not duplicate_case_ids
        and not source_mismatch_ids
        and not adjudicator_overlap_ids
        and not reviewer_adjudicator_overlap_ids
        and not duplicate_ids
        and not unknown_case_ids
        and invalid_count == 0
    )
    return {
        "required_cases": len(cases),
        "complete_cases": len(complete_case_ids),
        "missing_case_ids": missing_case_ids,
        "duplicate_case_ids": duplicate_case_ids,
        "source_mismatch_case_ids": source_mismatch_ids,
        "adjudicator_reviewer_overlap_case_ids": adjudicator_overlap_ids,
        "reviewer_ids": reviewer_ids,
        "adjudicator_ids": adjudicator_ids,
        "reviewer_adjudicator_overlap_ids": reviewer_adjudicator_overlap_ids,
        "role_independence_complete": not reviewer_adjudicator_overlap_ids,
        "unknown_case_ids": unknown_case_ids,
        "duplicate_adjudication_ids": duplicate_ids,
        "valid_human_records": len(valid),
        "invalid_or_nonhuman_records_ignored": invalid_count,
        "complete": complete,
    }


def human_freeze_readiness(
    manifest_path: Path | None,
    repository_root: Path,
    required_paths: dict[str, Path | None],
) -> dict[str, Any]:
    missing_inputs = sorted(name for name, path in required_paths.items() if path is None)
    base = {
        "manifest": str(manifest_path) if manifest_path else None,
        "required_input_categories": sorted(required_paths),
        "missing_input_categories": missing_inputs,
        "input_paths_are_distinct": False,
        "required_files": [],
        "required_files_missing_from_manifest": [],
        "manifest_hashes_valid": False,
        "metadata_valid": False,
        "complete": False,
    }
    if manifest_path is None or missing_inputs or not manifest_path.exists():
        return base

    root = repository_root.resolve()
    resolved_inputs = [path.resolve() for path in required_paths.values() if path]
    base["input_paths_are_distinct"] = len(resolved_inputs) == len(set(resolved_inputs))
    required_files: list[str] = []
    try:
        for path in resolved_inputs:
            targets = (
                sorted([*path.glob("*.jsonl"), *path.glob("*.json")])
                if path.is_dir()
                else [path]
            )
            if not targets:
                raise ValueError(f"No frozen records found under {path}")
            for target in targets:
                required_files.append(target.resolve().relative_to(root).as_posix())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        verification = verify_manifest(manifest_path, root)
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return base

    listed = {item.get("path") for item in manifest.get("files", [])}
    missing_from_manifest = sorted(set(required_files) - listed)
    status = manifest.get("status", {})
    metadata_valid = (
        manifest.get("freeze_scope") == "human_reviewed_benchmark_inputs"
        and status.get("human_inputs_frozen") is True
        and status.get("candidate_only") is False
        and status.get("privacy_review_status") == "passed"
        and status.get("holdout_policy") == "not_used_for_tuning"
    )
    complete = (
        base["input_paths_are_distinct"]
        and not missing_from_manifest
        and verification["valid"]
        and metadata_valid
    )
    return {
        **base,
        "required_files": sorted(set(required_files)),
        "required_files_missing_from_manifest": missing_from_manifest,
        "manifest_hashes_valid": verification["valid"],
        "manifest_files": verification["files"],
        "manifest_matched": verification["matched"],
        "metadata_valid": metadata_valid,
        "complete": complete,
    }


def reviewed_errors(output_review_records: list[dict[str, Any]]) -> tuple[dict[str, int], list[dict[str, Any]]]:
    counts = {code: 0 for code in ERROR_CODES}
    failures: list[dict[str, Any]] = []
    for review in human_output_reviews(output_review_records):
        for error in review.get("errors", []):
            code = error.get("code")
            if code not in counts:
                continue
            counts[code] += 1
            failures.append(
                {
                    "case_id": review["case_id"],
                    "packet_id": review.get("packet_id"),
                    "source": "human_output_review",
                    "code": code,
                    "severity": error.get("severity"),
                    "target": error.get("target"),
                    "rationale": error.get("rationale"),
                }
            )
    return counts, failures


def dataset_audit(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "cases": len(cases),
        "splits": dict(sorted(Counter(case.get("split", "legacy") for case in cases).items())),
        "double_review_required": sum(bool(case.get("double_review_required")) for case in cases),
        "human_review_statuses_declared_by_cases": dict(
            sorted(Counter(case.get("human_review_status", "legacy") for case in cases).items())
        ),
        "privacy_statuses": dict(
            sorted(Counter(case.get("privacy_status", "legacy") for case in cases).items())
        ),
    }


def _field_context(case: dict[str, Any]) -> dict[str, Any]:
    field = case["field"]
    return {
        "crop": field.get("crop"),
        "stage_in_memory": field.get("stage"),
        "risk_flags": field.get("risk_flags", []),
        "history": field.get("history", []),
        "weather": field.get("weather", {}),
    }


def reference_packet_id(case_id: str) -> str:
    return hashlib.sha256(
        f"reference:{case_id}:{SCHEMA_VERSION}".encode("utf-8")
    ).hexdigest()[:16]


def output_packet_id(case_id: str, system_alias: str) -> str:
    return hashlib.sha256(
        f"output:{case_id}:{system_alias}:{SCHEMA_VERSION}".encode("utf-8")
    ).hexdigest()[:16]


def make_reference_packet(case: dict[str, Any]) -> dict[str, Any]:
    """Build Phase A material without any system output or system identity."""

    return {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "reference_annotation",
        "packet_id": reference_packet_id(case["id"]),
        "case_id": case["id"],
        "note": case["note"],
        "field_context": _field_context(case),
    }


def make_output_review_packet(
    case: dict[str, Any],
    observation: StructuredObservation,
    status: str,
    missing: list[str],
    questions: list[str],
    score: float,
    rationale: list[str],
    tasks: list[TaskProposal],
    system_alias: str,
) -> dict[str, Any]:
    observation_payload = observation.model_dump(
        exclude={"field_id", "raw_text", "provider"}
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "output_review",
        "packet_id": output_packet_id(case["id"], system_alias),
        "reference_packet_id": reference_packet_id(case["id"]),
        "case_id": case["id"],
        "system_alias": system_alias,
        "note": case["note"],
        "field_context": _field_context(case),
        "output": {
            "observation": observation_payload,
            "status": status,
            "missing_critical": missing,
            "followup_questions": questions,
            "priority_score": score,
            "rationale": rationale,
            "proposed_tasks": [
                {
                    "task_index": index,
                    "title": task.title,
                    "priority": task.priority,
                    "due_hours": task.due_hours,
                    "rationale": task.rationale,
                    "requires_approval": task.requires_approval,
                    "status": task.status,
                }
                for index, task in enumerate(tasks)
            ],
            "official_alerts": [],
        },
    }


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records)
    path.write_text(payload + ("\n" if payload else ""), encoding="utf-8")
