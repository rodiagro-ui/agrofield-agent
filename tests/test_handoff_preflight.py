import ast
from pathlib import Path

import pytest

from agrofield_agent import handoff_preflight


HEADERS = {"Host": "127.0.0.1:18092", "Origin": handoff_preflight.ORIGIN,
           "Content-Type": "application/x-www-form-urlencoded"}


def test_matching_headers_allow_only_the_diagnostic():
    result = handoff_preflight.inspect_headers("/once", HEADERS, "/once")
    assert result["guard_would_accept"] is True
    assert result["api_execution_available"] is False
    assert result["external_requests"] == 0
    assert result["body_read"] is False


@pytest.mark.parametrize("name,value", [
    ("Origin", "null"), ("Origin", ""),
    ("Origin", "https://example.invalid"),
    ("Origin", "http://127.0.0.1:18093"),
    ("Host", "example.invalid"), ("Content-Type", "text/plain"),
])
def test_unknown_origin_host_or_type_is_not_accepted(name, value):
    result = handoff_preflight.inspect_headers("/once", {**HEADERS, name: value}, "/once")
    assert result["guard_would_accept"] is False
    assert result["api_execution_available"] is False


def test_missing_origin_and_wrong_route_fail_closed():
    headers = {k: v for k, v in HEADERS.items() if k != "Origin"}
    assert handoff_preflight.inspect_headers("/once", headers, "/once")["guard_would_accept"] is False
    assert handoff_preflight.inspect_headers("/other", HEADERS, "/once")["guard_would_accept"] is False


def test_diagnostic_imports_only_stdlib_not_application_or_api_clients():
    tree = ast.parse(Path(handoff_preflight.__file__).read_text(encoding="utf-8"))
    allowed = {"__future__", "argparse", "html", "http", "json", "secrets", "time", "typing"}
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module.split(".")[0])
    assert imports <= allowed
