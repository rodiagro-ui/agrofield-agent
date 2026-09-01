from __future__ import annotations

import argparse
import asyncio
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from agrofield_agent.benchmarking import (
    ERROR_CODES,
    REFERENCE_FIELDS,
    adjudication_readiness,
    dataset_audit,
    human_freeze_readiness,
    interview_readiness,
    load_cases,
    load_records,
    make_output_review_packet,
    make_reference_packet,
    reference_for_case,
    reference_status,
    review_readiness,
    reviewed_errors,
    reviewer_agreement,
    task_review_metrics,
    write_jsonl,
)
from agrofield_agent.models import FieldRecord, StructuredObservation
from agrofield_agent.policy import evaluate_policy
from agrofield_agent.services.extraction import LocalExtractionProvider


FIELDS = REFERENCE_FIELDS
NUMERIC_FIELDS = {
    "event_hours_ago",
    "sample_points",
    "affected_area_pct",
    "standing_water_pct",
    "water_duration_hours",
    "lodging_pct",
    "stem_damage_pct",
    "stand_count_per_m",
}


def _gate(
    passed: bool, actual: Any, requirement: str, failure: str
) -> dict[str, Any]:
    return {
        "passed": bool(passed),
        "actual": actual,
        "requirement": requirement,
        "failure_reason": None if passed else failure,
    }


def build_validation_gates(
    *,
    split: str | None,
    cases: list[dict[str, Any]],
    interviews: dict[str, Any],
    readiness: dict[str, Any],
    task_metrics: dict[str, Any],
    adjudication_status: dict[str, Any],
    agreement: dict[str, Any],
    reference_status_label: str,
    freeze_status: dict[str, Any],
    extraction_micro_f1: float,
    critical_omission_recall: float,
    unsupported_assertion_rate: float,
    evidence_quote_coverage: float,
    decision_gate_safety: float,
    priority_ndcg: float | None,
    human_approval_integrity: float,
) -> dict[str, dict[str, Any]]:
    """Build every binding gate; callers cannot bypass one with a partial report."""

    invalid_privacy_records = (
        interviews["invalid_or_nonhuman_records_ignored"]
        + readiness["invalid_or_nonhuman_records_ignored"]
        + task_metrics["invalid_or_nonhuman_records_ignored"]
        + adjudication_status["invalid_or_nonhuman_records_ignored"]
    )
    required_double_cases = sum(
        bool(case.get("double_review_required")) for case in cases
    )
    return {
        "full_frozen_dataset": _gate(
            split in (None, "all") and len(cases) >= 30 and required_double_cases >= 10,
            {
                "split": split or "all",
                "cases": len(cases),
                "double_cases": required_double_cases,
            },
            "all split, at least 30 cases and at least 10 fixed double-review cases",
            "The evaluation is a subset or lacks the required 30/10 benchmark design.",
        ),
        "human_interviews": _gate(
            interviews["complete"],
            interviews["valid_unique_interviews"],
            "3-5 unique, consented, sanitized human interviews",
            "Interview count, consent, sanitization, uniqueness, or privacy review is incomplete.",
        ),
        "reference_reviews": _gate(
            readiness["complete"],
            {
                "primary": readiness["primary_reviewed_cases"],
                "double": readiness["double_reviewed_cases"],
            },
            "one primary per case and one independent secondary for every fixed double case",
            "Primary or independent secondary reference reviews are missing, duplicated, or invalid.",
        ),
        "output_reviews": _gate(
            task_metrics["complete"],
            {
                "primary": task_metrics["complete_primary_output_review_cases"],
                "double": task_metrics["complete_double_output_review_cases"],
            },
            "one complete locked primary output review per case and one complete locked secondary per double case",
            "Output reviews, full task labels, Phase-A locks, or independent double reviews are incomplete.",
        ),
        "adjudications": _gate(
            adjudication_status["complete"],
            adjudication_status["complete_cases"],
            "one privacy-passed independent human adjudication per case linked to exact source reviews",
            "Adjudications are missing, duplicated, invalid, role-overlapping, or linked to the wrong reviews.",
        ),
        "reviewer_agreement": _gate(
            agreement["complete"],
            {
                "reference_pairs": agreement["double_annotated_case_pairs"],
                "output_pairs": agreement["double_reviewed_output_pairs"],
            },
            "agreement computed from every fixed reference and output pair",
            "At least one required reference or complete output pair is missing.",
        ),
        "adjudicated_reference": _gate(
            reference_status_label == "adjudicated_human_reference",
            reference_status_label,
            "all evaluation references are valid human adjudications",
            "At least one metric still uses a candidate or preliminary reference.",
        ),
        "privacy_controls": _gate(
            invalid_privacy_records == 0 and freeze_status["metadata_valid"],
            {
                "invalid_records": invalid_privacy_records,
                "freeze_metadata": freeze_status["metadata_valid"],
            },
            "all counted records privacy-passed plus independent final privacy status in the human freeze",
            "A supplied record is invalid/nonhuman or the final freeze lacks passed privacy metadata.",
        ),
        "human_input_freeze": _gate(
            freeze_status["complete"],
            {
                "hashes_valid": freeze_status["manifest_hashes_valid"],
                "metadata_valid": freeze_status["metadata_valid"],
                "missing_files": freeze_status["required_files_missing_from_manifest"],
            },
            "distinct human input files listed in a valid human-reviewed freeze with holdout declaration",
            "The human-input manifest, hashes, file coverage, privacy status, or holdout declaration is incomplete.",
        ),
        "extraction_micro_f1": _gate(
            extraction_micro_f1 >= 0.90,
            extraction_micro_f1,
            ">= 0.90",
            "Extraction micro-F1 is below 0.90.",
        ),
        "critical_omission_recall": _gate(
            critical_omission_recall >= 0.98,
            critical_omission_recall,
            ">= 0.98",
            "Critical omission recall is below 0.98.",
        ),
        "unsupported_assertion_rate": _gate(
            unsupported_assertion_rate <= 0.01,
            unsupported_assertion_rate,
            "<= 0.01",
            "Unsupported assertion rate exceeds 0.01.",
        ),
        "evidence_quote_coverage": _gate(
            evidence_quote_coverage >= 1.0,
            evidence_quote_coverage,
            "== 1.00",
            "At least one extracted fact lacks a literal evidence quote.",
        ),
        "decision_gate_safety": _gate(
            decision_gate_safety >= 1.0,
            decision_gate_safety,
            "== 1.00",
            "At least one critical omission was not blocked.",
        ),
        "priority_ndcg": _gate(
            priority_ndcg is not None and priority_ndcg >= 0.90,
            priority_ndcg,
            ">= 0.90",
            "Priority nDCG is unavailable or below 0.90.",
        ),
        "primary_task_precision": _gate(
            task_metrics["primary_task_precision"] is not None
            and task_metrics["primary_task_precision"] >= 0.90,
            task_metrics["primary_task_precision"],
            ">= 0.90 using primary reviews only",
            "Primary task precision is unavailable or below 0.90.",
        ),
        "human_approval_integrity": _gate(
            human_approval_integrity >= 1.0,
            human_approval_integrity,
            "== 1.00",
            "At least one task bypassed mandatory pending human approval.",
        ),
    }


def _equal(predicted: Any, gold: Any) -> bool:
    if isinstance(gold, (int, float)) and isinstance(predicted, (int, float)):
        return math.isclose(float(predicted), float(gold), abs_tol=0.01)
    return predicted == gold


def _missing(value: Any) -> bool:
    return value is None or value == "unknown"


def _dcg(relevances: list[float]) -> float:
    return sum((2**rel - 1) / math.log2(index + 2) for index, rel in enumerate(relevances))


def _valid_quote(observation: StructuredObservation, name: str) -> bool:
    quote = observation.evidence_quotes.get(name)
    return bool(quote and quote.strip() and quote.strip() in observation.raw_text)


def _append_error(
    errors: dict[str, list[dict[str, Any]]],
    case_id: str,
    code: str,
    target: str,
    expected: Any,
    predicted: Any,
    rationale: str,
) -> None:
    item = {
        "code": code,
        "target": target,
        "expected": expected,
        "predicted": predicted,
        "rationale": rationale,
        "source": "automated_comparison",
    }
    if item not in errors[case_id]:
        errors[case_id].append(item)


def _field_errors(
    case_id: str,
    observation: StructuredObservation,
    reference: dict[str, Any],
    errors: dict[str, list[dict[str, Any]]],
) -> None:
    for name in FIELDS:
        predicted = getattr(observation, name)
        expected = reference.get(name)
        if _missing(expected) and not _missing(predicted):
            _append_error(
                errors,
                case_id,
                "E4",
                name,
                expected,
                predicted,
                "El sistema produjo un valor donde la referencia no contiene un hecho.",
            )
        elif not _missing(expected) and _missing(predicted):
            _append_error(
                errors,
                case_id,
                "E5",
                name,
                expected,
                predicted,
                "El sistema omitió un hecho presente en la referencia.",
            )
        elif not _missing(expected) and not _equal(predicted, expected):
            code = "E2" if name in NUMERIC_FIELDS else "E1"
            _append_error(
                errors,
                case_id,
                code,
                name,
                expected,
                predicted,
                "El valor extraído no coincide con la referencia.",
            )
            if name in NUMERIC_FIELDS and any(
                other != name
                and not _missing(other_value)
                and _equal(predicted, other_value)
                for other, other_value in reference.items()
            ):
                _append_error(
                    errors,
                    case_id,
                    "E3",
                    name,
                    expected,
                    predicted,
                    "El valor coincide con otro campo de la referencia y puede estar mal atribuido.",
                )
        if not _missing(predicted) and not _valid_quote(observation, name):
            _append_error(
                errors,
                case_id,
                "E4",
                name,
                "cita literal contenida en la nota",
                observation.evidence_quotes.get(name),
                "El valor no tiene una cita literal verificable en la nota.",
            )


async def run(
    path: Path,
    *,
    split: str | None = None,
    case_annotations_path: Path | None = None,
    output_reviews_path: Path | None = None,
    adjudications_path: Path | None = None,
    interview_records_path: Path | None = None,
    human_freeze_manifest_path: Path | None = None,
    freeze_root: Path | None = None,
    reference_packet_out: Path | None = None,
    output_packet_out: Path | None = None,
    system_alias: str = "system-unlabeled",
) -> dict[str, Any]:
    if (
        reference_packet_out is not None
        and output_packet_out is not None
        and reference_packet_out.resolve() == output_packet_out.resolve()
    ):
        raise ValueError("Phase A and Phase B packets must use different files")
    cases = load_cases(path, split)
    if not cases:
        raise ValueError("The selected dataset contains no cases")
    case_annotations = load_records(case_annotations_path)
    output_reviews = load_records(output_reviews_path)
    adjudications = load_records(adjudications_path)
    interview_records = load_records(interview_records_path)

    provider = LocalExtractionProvider()
    tp = fp = fn = unsupported = predicted_non_null = 0
    omission_tp = omission_fn = safe_blocks = unsafe_missing_cases = 0
    traceable_predictions = approval_integrity_cases = 0
    latencies: list[float] = []
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    automatic_errors: dict[str, list[dict[str, Any]]] = defaultdict(list)
    source_labels: list[str] = []
    reference_packets: list[dict[str, Any]] = []
    output_packets: list[dict[str, Any]] = []
    expected_task_counts: dict[str, int] = {}

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
        status, missing, questions, score, rationale, tasks = evaluate_policy(field, observation)
        reference, expected_missing_list, relevance, source = reference_for_case(
            case, case_annotations, adjudications
        )
        source_labels.append(source)

        for name in FIELDS:
            predicted = getattr(observation, name)
            expected = reference.get(name)
            if not _missing(predicted):
                predicted_non_null += 1
                traceable_predictions += int(_valid_quote(observation, name))
            if _missing(expected):
                if not _missing(predicted):
                    fp += 1
                    unsupported += 1
            elif _missing(predicted):
                fn += 1
            elif _equal(predicted, expected):
                tp += 1
            else:
                fp += 1
                fn += 1

        expected_missing = set(expected_missing_list)
        actual_missing = set(missing)
        omission_tp += len(expected_missing & actual_missing)
        omission_fn += len(expected_missing - actual_missing)
        if expected_missing:
            unsafe_missing_cases += 1
            safe_blocks += int(status == "blocked")
        if expected_missing - actual_missing:
            for name in sorted(expected_missing - actual_missing):
                _append_error(
                    automatic_errors,
                    case["id"],
                    "E5",
                    name,
                    "flagged_missing",
                    "not_flagged",
                    "Una omisión crítica esperada no fue señalada.",
                )
        if expected_missing and status != "blocked":
            _append_error(
                automatic_errors,
                case["id"],
                "E7",
                "decision_gate",
                "blocked",
                status,
                "El caso contiene omisiones críticas, pero la decisión no quedó bloqueada.",
            )

        approval_intact = all(
            task.requires_approval and task.status == "pending" for task in tasks
        )
        expected_task_counts[case["id"]] = len(tasks)
        approval_integrity_cases += int(approval_intact)
        if not approval_intact:
            _append_error(
                automatic_errors,
                case["id"],
                "E7",
                "task_approval",
                "requires_approval and pending",
                [task.model_dump() for task in tasks],
                "Una tarea evita la aprobación humana o ya aparece ejecutada.",
            )
        if observation.access_safe is False and any(
            "escalar acceso inseguro" not in task.title.lower() for task in tasks
        ):
            _append_error(
                automatic_errors,
                case["id"],
                "E7",
                "unsafe_access_task",
                "solo escalamiento de seguridad",
                [task.title for task in tasks],
                "Con acceso inseguro solo corresponde escalar sin ingresar.",
            )

        _field_errors(case["id"], observation, reference, automatic_errors)

        group = case.get("ranking_group") or case.get("scenario")
        if group and relevance is not None:
            groups[str(group)].append(
                {"case_id": case["id"], "score": score, "relevance": float(relevance)}
            )

        if reference_packet_out is not None:
            reference_packets.append(make_reference_packet(case))
        if output_packet_out is not None:
            output_packets.append(
                make_output_review_packet(
                    case,
                    observation,
                    status,
                    missing,
                    questions,
                    score,
                    rationale,
                    tasks,
                    system_alias,
                )
            )

    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    omission_recall = (
        omission_tp / (omission_tp + omission_fn)
        if omission_tp + omission_fn
        else 1.0
    )
    ndcgs: list[float] = []
    for pairs in groups.values():
        predicted_order = sorted(
            pairs, key=lambda item: (item["score"], item["case_id"]), reverse=True
        )
        ideal_order = sorted(
            pairs, key=lambda item: (item["relevance"], item["case_id"]), reverse=True
        )
        predicted_relevance = [item["relevance"] for item in predicted_order]
        ideal_relevance = [item["relevance"] for item in ideal_order]
        ideal_dcg = _dcg(ideal_relevance)
        ndcgs.append(_dcg(predicted_relevance) / ideal_dcg if ideal_dcg else 1.0)
        ideal_position = {
            item["case_id"]: position for position, item in enumerate(ideal_order)
        }
        for position, item in enumerate(predicted_order):
            expected_position = ideal_position[item["case_id"]]
            if position != expected_position:
                _append_error(
                    automatic_errors,
                    item["case_id"],
                    "E6",
                    "priority_rank",
                    expected_position + 1,
                    position + 1,
                    "La posición prevista difiere del orden de referencia dentro del grupo.",
                )

    if reference_packet_out is not None:
        write_jsonl(reference_packet_out, reference_packets)
    if output_packet_out is not None:
        write_jsonl(output_packet_out, output_packets)

    task_metrics = task_review_metrics(
        cases, output_reviews, expected_task_counts, case_annotations
    )
    human_error_counts, human_failures = reviewed_errors(output_reviews)
    automatic_error_counts = {
        code: sum(
            error["code"] == code
            for case_errors in automatic_errors.values()
            for error in case_errors
        )
        for code in ERROR_CODES
    }
    error_matrix = {
        code: {
            "automated": automatic_error_counts[code],
            "human_review": human_error_counts[code],
            "total": automatic_error_counts[code] + human_error_counts[code],
        }
        for code in ERROR_CODES
    }
    automatic_failures = [
        {"case_id": case_id, **error}
        for case_id in sorted(automatic_errors)
        for error in automatic_errors[case_id]
    ]
    adverse_failures = automatic_failures + human_failures

    status_label, status_counts = reference_status(source_labels)
    readiness = review_readiness(cases, case_annotations)
    agreement = reviewer_agreement(
        cases, case_annotations, output_reviews, expected_task_counts
    )
    interviews = interview_readiness(interview_records)
    adjudication_status = adjudication_readiness(
        cases, case_annotations, adjudications
    )
    freeze_status = human_freeze_readiness(
        human_freeze_manifest_path,
        freeze_root or Path.cwd(),
        {
            "dataset": path,
            "interviews": interview_records_path,
            "case_annotations": case_annotations_path,
            "output_reviews": output_reviews_path,
            "adjudications": adjudications_path,
        },
    )

    rounded_precision = round(precision, 4)
    rounded_recall = round(recall, 4)
    rounded_f1 = round(f1, 4)
    rounded_omission_recall = round(omission_recall, 4)
    unsupported_rate = (
        round(unsupported / predicted_non_null, 4) if predicted_non_null else 0.0
    )
    evidence_coverage = (
        round(traceable_predictions / predicted_non_null, 4)
        if predicted_non_null
        else 1.0
    )
    gate_safety = (
        round(safe_blocks / unsafe_missing_cases, 4)
        if unsafe_missing_cases
        else 1.0
    )
    approval_integrity = round(approval_integrity_cases / len(cases), 4)
    priority_ndcg = round(statistics.mean(ndcgs), 4) if ndcgs else None

    validation_gates = build_validation_gates(
        split=split,
        cases=cases,
        interviews=interviews,
        readiness=readiness,
        task_metrics=task_metrics,
        adjudication_status=adjudication_status,
        agreement=agreement,
        reference_status_label=status_label,
        freeze_status=freeze_status,
        extraction_micro_f1=rounded_f1,
        critical_omission_recall=rounded_omission_recall,
        unsupported_assertion_rate=unsupported_rate,
        evidence_quote_coverage=evidence_coverage,
        decision_gate_safety=gate_safety,
        priority_ndcg=priority_ndcg,
        human_approval_integrity=approval_integrity,
    )
    benchmark_validated = all(item["passed"] for item in validation_gates.values())

    result = {
        "cases": len(cases),
        "extraction_precision": rounded_precision,
        "extraction_recall": rounded_recall,
        "extraction_micro_f1": rounded_f1,
        "critical_omission_recall": rounded_omission_recall,
        "unsupported_assertion_rate": unsupported_rate,
        "evidence_quote_coverage": evidence_coverage,
        "decision_gate_safety": gate_safety,
        "human_approval_integrity": approval_integrity,
        "priority_ndcg": priority_ndcg,
        "task_precision": task_metrics["task_precision"],
        "task_review": task_metrics,
        "latency_ms_p50": round(statistics.median(latencies), 3),
        "latency_ms_max": round(max(latencies), 3),
        "provider": "local/deterministic-es-v0.1",
        "estimated_cost_usd": 0.0,
        "reference_status": status_label,
        "reference_status_counts": status_counts,
        "dataset_audit": dataset_audit(cases),
        "human_review_readiness": readiness,
        "human_interview_readiness": interviews,
        "human_adjudication_readiness": adjudication_status,
        "human_freeze_readiness": freeze_status,
        "reviewer_agreement": agreement,
        "error_matrix": error_matrix,
        "adverse_failure_count": len(adverse_failures),
        "adverse_failures": adverse_failures,
        "validation_gates": validation_gates,
        "benchmark_validated": benchmark_validated,
        "warning": (
            "Local deterministic result. It is not a Nemotron result and is not "
            "an agronomist-validated benchmark."
            if not benchmark_validated
            else "Human reference is adjudicated; provider remains local/deterministic-es-v0.1."
        ),
    }
    if reference_packet_out is not None:
        result["reference_packet"] = {
            "path": str(reference_packet_out),
            "packets": len(reference_packets),
            "phase": "A",
            "system_output_included": False,
            "system_alias_included": False,
            "provider_metadata_included": False,
            "split_metadata_included": False,
        }
    if output_packet_out is not None:
        result["output_packet"] = {
            "path": str(output_packet_out),
            "packets": len(output_packets),
            "phase": "B",
            "system_alias": system_alias,
            "provider_metadata_included": False,
            "split_metadata_included": False,
        }
    return result


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Evaluate AgroField extraction, policy, and blind human review"
    )
    parser.add_argument("dataset", type=Path)
    parser.add_argument(
        "--split", choices=("all", "development", "holdout"), default="all"
    )
    parser.add_argument("--case-annotations", type=Path)
    parser.add_argument("--output-reviews", type=Path)
    parser.add_argument("--adjudications", type=Path)
    parser.add_argument("--interviews", type=Path)
    parser.add_argument(
        "--human-freeze-manifest",
        type=Path,
        help="Manifest that freezes all sanitized human inputs before evaluation.",
    )
    parser.add_argument(
        "--freeze-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root used to resolve paths listed by the human freeze.",
    )
    parser.add_argument(
        "--reference-packet-out",
        type=Path,
        help="Write Phase A note/context packets with no system output.",
    )
    parser.add_argument(
        "--output-packet-out",
        type=Path,
        help="Write Phase B system-output packets for use after Phase A is locked.",
    )
    parser.add_argument("--system-alias", default="system-unlabeled")
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--require-validated",
        action="store_true",
        help="Exit non-zero unless all human-review validation gates are complete.",
    )
    args = parser.parse_args()
    result = asyncio.run(
        run(
            args.dataset,
            split=args.split,
            case_annotations_path=args.case_annotations,
            output_reviews_path=args.output_reviews,
            adjudications_path=args.adjudications,
            interview_records_path=args.interviews,
            human_freeze_manifest_path=args.human_freeze_manifest,
            freeze_root=args.freeze_root,
            reference_packet_out=args.reference_packet_out,
            output_packet_out=args.output_packet_out,
            system_alias=args.system_alias,
        )
    )
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    if args.require_validated and not result["benchmark_validated"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
