from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

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


def _valid_human_annotation(record: dict[str, Any]) -> bool:
    return (
        record.get("review_origin") == "human"
        and record.get("blind") is True
        and record.get("consent_to_anonymous_results") is True
        and bool(record.get("reviewer_id"))
        and bool(record.get("case_id"))
        and all(name in record.get("reference_fields", {}) for name in REFERENCE_FIELDS)
    )


def _valid_human_output_review(record: dict[str, Any]) -> bool:
    return (
        record.get("review_origin") == "human"
        and record.get("blind") is True
        and record.get("consent_to_anonymous_results") is True
        and bool(record.get("reviewer_id"))
        and bool(record.get("case_id"))
    )


def _valid_human_adjudication(
    record: dict[str, Any], *, double_review_required: bool
) -> bool:
    required_sources = 2 if double_review_required else 1
    return (
        record.get("status") == "adjudicated"
        and record.get("adjudication_origin") == "human"
        and record.get("consent_to_anonymous_results") is True
        and bool(record.get("adjudicator_id"))
        and len(set(record.get("source_review_ids", []))) >= required_sources
        and all(
            name in record.get("final_reference_fields", {})
            for name in REFERENCE_FIELDS
        )
    )


def human_case_annotations(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if _valid_human_annotation(record)]


def human_output_reviews(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if _valid_human_output_review(record)]


def reference_for_case(
    case: dict[str, Any],
    annotations: list[dict[str, Any]],
    adjudications: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[str], float | None, str]:
    case_id = case["id"]
    adjudicated = [
        item
        for item in adjudications
        if item.get("case_id") == case_id
        and _valid_human_adjudication(
            item, double_review_required=bool(case.get("double_review_required"))
        )
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
        [item for item in human_case_annotations(annotations) if item.get("case_id") == case_id],
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


def _review_pairs(
    records: list[dict[str, Any]], group_keys: tuple[str, ...]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[tuple(record.get(key) for key in group_keys)].append(record)
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for group in groups.values():
        by_reviewer: dict[str, dict[str, Any]] = {}
        for record in sorted(group, key=lambda item: item.get("review_id", "")):
            by_reviewer.setdefault(record["reviewer_id"], record)
        pairs.extend(combinations(by_reviewer.values(), 2))
    return pairs


def reviewer_agreement(
    case_annotation_records: list[dict[str, Any]],
    output_review_records: list[dict[str, Any]],
) -> dict[str, Any]:
    annotations = human_case_annotations(case_annotation_records)
    outputs = human_output_reviews(output_review_records)
    annotation_pairs = _review_pairs(annotations, ("case_id",))

    missing_a: list[str] = []
    missing_b: list[str] = []
    categorical: dict[str, tuple[list[str], list[str]]] = {
        name: ([], []) for name in CATEGORICAL_FIELDS
    }
    numeric_equal = numeric_total = 0
    for first, second in annotation_pairs:
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
            elif isinstance(value_a, (int, float)) and isinstance(value_b, (int, float)):
                numeric_equal += int(math.isclose(float(value_a), float(value_b), abs_tol=0.01))

    output_pairs = _review_pairs(outputs, ("case_id", "packet_id"))
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
    for first, second in output_pairs:
        for name in output_fields:
            output_labels[name][0].append(str(first.get(name)))
            output_labels[name][1].append(str(second.get(name)))
        tasks_a = {item.get("task_index"): item.get("classification") for item in first.get("task_labels", [])}
        tasks_b = {item.get("task_index"): item.get("classification") for item in second.get("task_labels", [])}
        for task_index in sorted(set(tasks_a) & set(tasks_b), key=str):
            task_a.append(str(tasks_a[task_index]))
            task_b.append(str(tasks_b[task_index]))

    nominal_pairs = len(missing_a) + sum(len(values[0]) for values in categorical.values())
    nominal_disagreements = sum(a != b for a, b in zip(missing_a, missing_b, strict=True))
    nominal_disagreements += sum(
        sum(a != b for a, b in zip(values[0], values[1], strict=True))
        for values in categorical.values()
    )
    return {
        "status": "available" if annotation_pairs or output_pairs else "pending_human_double_review",
        "double_annotated_case_pairs": len(annotation_pairs),
        "double_reviewed_output_pairs": len(output_pairs),
        "raw_disagreement": round(nominal_disagreements / nominal_pairs, 4) if nominal_pairs else None,
        "missing_critical": _metric(missing_a, missing_b),
        "categorical_fields": {
            name: _metric(values[0], values[1]) for name, values in categorical.items()
        },
        "numeric_fields": {
            "paired_items": numeric_total,
            "raw_agreement": round(numeric_equal / numeric_total, 4) if numeric_total else None,
            "raw_disagreement": round(1 - numeric_equal / numeric_total, 4) if numeric_total else None,
            "cohens_kappa": None,
        },
        "output_judgements": {
            name: _metric(values[0], values[1]) for name, values in output_labels.items()
        },
        "task_classification": _metric(task_a, task_b),
    }


def review_readiness(
    cases: list[dict[str, Any]], annotation_records: list[dict[str, Any]]
) -> dict[str, Any]:
    annotations = human_case_annotations(annotation_records)
    reviewers_by_case: dict[str, set[str]] = defaultdict(set)
    for annotation in annotations:
        reviewers_by_case[annotation["case_id"]].add(annotation["reviewer_id"])
    primary = sum(bool(reviewers_by_case.get(case["id"])) for case in cases)
    double_required = [case for case in cases if case.get("double_review_required")]
    doubled = sum(len(reviewers_by_case.get(case["id"], set())) >= 2 for case in double_required)
    return {
        "required_primary_cases": len(cases),
        "primary_reviewed_cases": primary,
        "required_double_review_cases": len(double_required),
        "double_reviewed_cases": doubled,
        "complete": primary == len(cases) and doubled == len(double_required),
        "invalid_or_nonhuman_records_ignored": len(annotation_records) - len(annotations),
    }


def task_review_metrics(output_review_records: list[dict[str, Any]]) -> dict[str, Any]:
    reviews = human_output_reviews(output_review_records)
    counts: Counter[str] = Counter()
    for review in reviews:
        for item in review.get("task_labels", []):
            label = item.get("classification")
            if label in TASK_CLASSIFICATIONS:
                counts[label] += 1
    denominator = sum(counts.values())
    return {
        "task_precision": round(counts["appropriate"] / denominator, 4) if denominator else None,
        "task_review_counts": {label: counts[label] for label in sorted(TASK_CLASSIFICATIONS)},
        "reviewed_task_labels": denominator,
        "status": "human_output_reviews" if denominator else "pending_human_output_review",
        "invalid_or_nonhuman_records_ignored": len(output_review_records) - len(reviews),
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


def make_blind_packet(
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
    packet_id = hashlib.sha256(
        f"{case['id']}:{system_alias}".encode("utf-8")
    ).hexdigest()[:16]
    field = case["field"]
    observation_payload = observation.model_dump(
        exclude={"field_id", "raw_text", "provider"}
    )
    return {
        "schema_version": "1.0.0-candidate",
        "packet_id": packet_id,
        "case_id": case["id"],
        "system_alias": system_alias,
        "note": case["note"],
        "field_context": {
            "crop": field.get("crop"),
            "stage_in_memory": field.get("stage"),
            "risk_flags": field.get("risk_flags", []),
            "history": field.get("history", []),
            "weather": field.get("weather", {}),
        },
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
