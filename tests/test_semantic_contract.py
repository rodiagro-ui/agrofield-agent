"""Synthetic reference/contract tests, not tests of live model quality."""

import copy
import json
from pathlib import Path

import httpx
import pytest

from agrofield_agent.evidence import source_catalog
from agrofield_agent.extraction_contract import EVIDENCE_FIELDS, FIELD_DESCRIPTIONS, PROFILE_ID
from agrofield_agent.freeze import canonical_sha256, verify_manifest
from agrofield_agent.nebius_smoke import ContractViolation, build_payload, strict_observation_schema
from agrofield_agent.semantic_preflight import check_cases, historical_plan

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "fixtures/development/semantic_v2/cases.jsonl"
CASES = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines()]


@pytest.mark.parametrize("case", CASES, ids=[case["case_id"] for case in CASES])
def test_synthetic_reference_is_representable_and_request_fits_budget(case):
    result = check_cases([case], historical_plan())
    assert result["checks"][0]["reference_contract_valid"] is True
    assert result["max_serialized_request_bytes"] + 1024 <= 16384
    assert result["nemotron_quality"] is None
    assert result["benchmark_validated"] is False


def test_all_fields_have_instructions_without_relaxing_the_wire_schema():
    properties = strict_observation_schema(CASES[0]["note"])["properties"]
    for name in EVIDENCE_FIELDS:
        assert properties[name]["description"] == FIELD_DESCRIPTIONS[name]
        assert len(properties[name]["description"]) > 80
    assert properties["event_type"]["enum"] == ["flooding", "hail", "wind", "mixed", "none", "unknown"]
    assert properties["event_hours_ago"]["anyOf"][0]["minimum"] == 0
    assert properties["sample_points"]["anyOf"][0]["minimum"] == 0


def test_note_stays_untrusted_user_data_and_references_never_enter_request():
    case = CASES[11]  # Deliberate instruction injection inside synthetic note.
    payload = build_payload(case["note"], historical_plan())
    assert len(payload["messages"]) == 2
    system, user = payload["messages"]
    assert system["role"] == "system"
    assert PROFILE_ID in system["content"]
    assert case["note"] not in system["content"]
    assert user["role"] == "user"
    assert json.loads(user["content"]) == {"sources": source_catalog(case["note"])}
    assert case["rationale"] not in json.dumps(payload, ensure_ascii=False)
    assert "expected" not in json.loads(user["content"])
    assert payload["tool_choice"]["function"]["name"] == "record_field_observation"


def test_preflight_never_uses_http_or_claims_model_quality(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Offline preflight must never construct an HTTP client")
    monkeypatch.setattr(httpx, "AsyncClient", forbidden)
    monkeypatch.setattr(httpx, "Client", forbidden)
    result = check_cases(CASES, historical_plan())
    assert result["cases"] == 20
    assert result["network_request_sent"] is False
    assert result["human_reviews"] == 0
    assert result["nemotron_quality"] is None
    assert result["benchmark_validated"] is False
    assert all(result["observed_reference_counts"][field] > 0 for field in EVIDENCE_FIELDS)
    assert all(result["unknown_reference_counts"][field] > 0 for field in EVIDENCE_FIELDS)


@pytest.mark.parametrize("key,value", [
    ("split", "holdout"), ("reference_origin", "human_review"),
])
def test_preflight_rejects_mislabeled_data(key, value):
    case = copy.deepcopy(CASES[0])
    case[key] = value
    with pytest.raises(ValueError, match="AI-authored synthetic development"):
        check_cases([case], historical_plan())


def test_incomplete_and_untraceable_references_do_not_count():
    case = copy.deepcopy(CASES[0])
    case["expected"].pop("event_hours_ago")
    with pytest.raises(ValueError, match="all 12"):
        check_cases([case], historical_plan())
    case = copy.deepcopy(CASES[0])
    case["evidence_sources"]["event_hours_ago"] = ["S99"]
    with pytest.raises(ContractViolation, match="invalid evidence source"):
        check_cases([case], historical_plan())


def test_empty_or_duplicate_reference_sets_are_rejected():
    with pytest.raises(ValueError, match="must not be empty"):
        check_cases([], historical_plan())
    with pytest.raises(ValueError, match="IDs must be nonempty and unique"):
        check_cases([CASES[0], CASES[0]], historical_plan())
    case = copy.deepcopy(CASES[0])
    case["case_id"] = "unique-id-same-note"
    with pytest.raises(ValueError, match="notes must be unique"):
        check_cases([CASES[0], case], historical_plan())


def test_development_notes_are_new_without_reading_frozen_labels():
    # Compare note strings only; no reference labels or holdout errors are used.
    notes = {case["note"].strip() for case in CASES}
    for relative in ("fixtures/eval_cases.jsonl", "benchmark/agronomy_blind_v1/data/cases.jsonl"):
        records = [json.loads(line) for line in (ROOT / relative).read_text(encoding="utf-8").splitlines()]
        assert all(record["note"].strip() not in notes for record in records)
    assert (ROOT / "fixtures/nebius_smoke_note.txt").read_text(encoding="utf-8").strip() not in notes


def test_request_hash_changes_when_note_or_profile_changes(monkeypatch):
    baseline = check_cases([CASES[0]], historical_plan())["checks"][0]["request_payload_sha256"]
    changed = copy.deepcopy(CASES[0])
    changed["note"] += " Nota adicional sin mediciones."
    assert check_cases([changed], historical_plan())["checks"][0]["request_payload_sha256"] != baseline
    import agrofield_agent.nebius_smoke as smoke
    monkeypatch.setattr(smoke, "SYSTEM_PROMPT", smoke.SYSTEM_PROMPT + " Cambio de perfil de prueba.")
    assert check_cases([CASES[0]], historical_plan())["checks"][0]["request_payload_sha256"] != baseline


def test_candidate_freeze_and_saved_preflight_match_without_claiming_human_evidence():
    manifest_path = DATASET.parent / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["freeze_scope"] == "synthetic_development_contract_not_human_benchmark"
    assert manifest["extraction_profile"] == PROFILE_ID
    assert manifest["candidate_live_calls"] == manifest["human_reviews"] == 0
    assert manifest["live_authorized"] is manifest["benchmark_validated"] is False
    assert verify_manifest(manifest_path, ROOT)["valid"] is True
    saved = json.loads((DATASET.parent / "preflight.json").read_text(encoding="utf-8"))
    current = check_cases(CASES, historical_plan())
    current["dataset_canonical_sha256"] = canonical_sha256(DATASET)
    assert current == saved
