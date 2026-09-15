import asyncio
import copy
import json
from pathlib import Path

import pytest

from agrofield_agent.smoke_audit import audit, compare_fields

ROOT = Path(__file__).resolve().parents[1]


def inputs():
    return (
        (ROOT / "fixtures/nebius_smoke_note.txt").read_text(encoding="utf-8"),
        json.loads((ROOT / "docs/submission/evidence/nebius-source-anchor-smoke-2026-09-14.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "fixtures/nebius_smoke_reference.json").read_text(encoding="utf-8")),
    )


def test_saved_live_failure_is_not_hidden_by_perfect_literal_quotes():
    result = asyncio.run(audit(*inputs()))
    assert result["saved_quote_literal_fraction"] == 1.0
    assert result["saved_nebius"]["correct_observed"] == 4
    assert result["saved_nebius"]["missing"] == 3
    assert result["saved_nebius"]["wrong_value"] == 1
    assert result["saved_nebius"]["unsupported"] == 1
    assert result["local"]["correct_observed"] == 8
    assert result["local"]["errors"] == []
    assert result["network_request_sent"] is False
    assert result["benchmark_validated"] is False


def test_audit_rejects_response_for_a_different_note():
    note, saved, reference = inputs()
    with pytest.raises(ValueError, match="does not match"):
        asyncio.run(audit(note + " Sin granizo.", saved, reference))


def test_audit_cannot_skip_fields_or_treat_boolean_as_quantity():
    _, _, reference = inputs()
    expected = reference["expected"]
    changed = copy.deepcopy(expected)
    changed["sample_points"] = True
    assert compare_fields(changed, expected)["wrong_value"] == 1
    changed.pop("general_condition")
    with pytest.raises(ValueError, match="complete 12-field"):
        compare_fields(changed, expected)
