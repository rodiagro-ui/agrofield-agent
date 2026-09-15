import asyncio
import json
from decimal import Decimal

import httpx
import pytest
from fastapi.testclient import TestClient

import agrofield_agent.app as app_module
from agrofield_agent.app import PROJECT_ROOT
from agrofield_agent.config import DEFAULT_NEBIUS_BASE_URL, Settings
from agrofield_agent.models import ObservationDraft
from agrofield_agent.nebius_smoke import (
    CONFIRMATION_PHRASE,
    ContractViolation,
    GuardedNebiusExtractionProvider,
    PreflightBlocked,
    SmokePlan,
    UpstreamRequestFailure,
    _validate_evidence,
    execute_one_request,
    preflight,
    provider_for_application,
    require_live_confirmation,
    strict_observation_schema,
)
from agrofield_agent.repository import Repository
from agrofield_agent.services.extraction import LocalExtractionProvider


NOTE = (
    "Soja V3. Tormenta hace 18 horas, acceso seguro. Recorrí 6 puntos. "
    "El agua parada afecta 35% del lote desde hace 14 horas."
)


def plan(**changes):
    values = {
        "model": "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
        "base_url": DEFAULT_NEBIUS_BASE_URL,
        "max_completion_tokens": 1024,
        "prompt_token_budget": 16384,
        "input_price_per_million": Decimal("0.06"),
        "output_price_per_million": Decimal("0.24"),
        "max_cost_usd": Decimal("0.01"),
        "reasoning_effort": "none",
    }
    values.update(changes)
    return SmokePlan(**values)


def make_settings(tmp_path, *, provider="local", api_key=None):
    return Settings(
        provider=provider,
        database_path=tmp_path / "test.sqlite3",
        nebius_api_key=api_key,
        nebius_base_url=DEFAULT_NEBIUS_BASE_URL,
        nebius_model="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
        tavily_api_key=None,
        tavily_include_domains=(),
    )


def valid_body(arguments=None):
    arguments = arguments or {
        "crop_stage": "V3",
        "event_type": "flooding",
        "event_hours_ago": 18,
        "access_safe": True,
        "sample_points": 6,
        "affected_area_pct": 35,
        "standing_water_pct": 35,
        "water_duration_hours": 14,
        "lodging_pct": None,
        "stem_damage_pct": None,
        "stand_count_per_m": None,
        "general_condition": "unknown",
        "note_sources": [],
        "evidence_sources": {
            "crop_stage": ["S01"],
            "event_type": ["S04"],
            "event_hours_ago": ["S02"],
            "access_safe": ["S02"],
            "sample_points": ["S03"],
            "affected_area_pct": ["S04"],
            "standing_water_pct": ["S04"],
            "water_duration_hours": ["S04"],
            "lodging_pct": [],
            "stem_damage_pct": [],
            "stand_count_per_m": [],
            "general_condition": [],
        },
        "uncertainties": [],
    }
    return {
        "id": "chatcmpl-test",
        "choices": [
            {
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call-test",
                            "type": "function",
                            "function": {
                                "name": "record_field_observation",
                                "arguments": json.dumps(arguments),
                            },
                        }
                    ],
                },
            }
        ],
        "usage": {"prompt_tokens": 900, "completion_tokens": 120, "total_tokens": 1020},
    }


def test_preflight_has_bounded_cost_and_forced_single_tool_call():
    payload, estimate = preflight(NOTE, plan())

    assert estimate.estimated_cost_ceiling_usd == Decimal("0.0012288")
    assert payload["max_completion_tokens"] == 1024
    assert payload["reasoning_effort"] == "none"
    assert payload["chat_template_kwargs"] == {"enable_thinking": False}
    assert "extra_body" not in payload
    assert payload["n"] == 1
    assert payload["stream"] is False
    assert payload["store"] is False
    assert payload["tool_choice"]["function"]["name"] == "record_field_observation"
    assert payload["tools"][0]["function"]["strict"] is True


def test_tool_schema_is_closed_required_and_has_no_pydantic_defaults():
    schema = strict_observation_schema(NOTE)

    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])
    evidence = schema["properties"]["evidence_sources"]
    assert evidence["additionalProperties"] is False
    assert set(evidence["required"]) == set(evidence["properties"])
    for field_schema in evidence["properties"].values():
        assert field_schema["items"]["enum"] == ["S01", "S02", "S03", "S04"]
    serialized = json.dumps(schema)
    assert '"default"' not in serialized
    assert '"$defs"' not in serialized
    assert '"$ref"' not in serialized
    assert '"minLength"' not in serialized
    assert '"uniqueItems"' not in serialized


def test_guarded_nemotron_profile_blocks_reasoning_before_network():
    with pytest.raises(PreflightBlocked, match="requires reasoning_effort=none"):
        preflight(NOTE, plan(reasoning_effort="low"))


def test_preflight_blocks_cost_above_cap_before_network():
    with pytest.raises(PreflightBlocked, match="exceeds authorized cap"):
        preflight(NOTE, plan(max_cost_usd=Decimal("0.0001")))


def test_preflight_rejects_non_nebius_endpoint():
    with pytest.raises(PreflightBlocked, match="HTTPS Token Factory"):
        preflight(NOTE, plan(base_url="https://example.com/v1"))


def test_confirmation_is_exact():
    require_live_confirmation(CONFIRMATION_PHRASE)
    with pytest.raises(PreflightBlocked, match="live request blocked"):
        require_live_confirmation(None)


def test_one_request_parses_tool_call_and_never_exposes_key_or_note():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        payload = json.loads(request.content)
        assert request.url == f"{DEFAULT_NEBIUS_BASE_URL}/chat/completions"
        assert request.headers["authorization"] == "Bearer test-secret"
        assert payload["max_completion_tokens"] == 1024
        assert payload["chat_template_kwargs"] == {"enable_thinking": False}
        assert "extra_body" not in payload
        assert payload["tool_choice"]["function"]["name"] == "record_field_observation"
        return httpx.Response(
            200,
            json=valid_body(),
            headers={"x-request-id": "req-test"},
        )

    result = asyncio.run(
        execute_one_request(
            NOTE,
            plan(),
            "test-secret",
            transport=httpx.MockTransport(handler),
        )
    )

    assert calls == 1
    assert result["status"] == "contract_pass"
    assert result["telemetry"]["request_id"] == "req-test"
    assert result["telemetry"]["input_tokens"] == 900
    assert result["telemetry"]["output_tokens"] == 120
    for quote in result["observation"]["evidence_quotes"].values():
        assert not quote or quote in NOTE
    assert result["observation"]["evidence_quotes"]["event_type"] == (
        "El agua parada afecta 35% del lote desde hace 14 horas."
    )
    serialized = json.dumps(result, ensure_ascii=False)
    assert "test-secret" not in serialized
    assert NOTE not in serialized


def test_empty_assistant_message_fails_after_exactly_one_request():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-empty",
                "choices": [
                    {
                        "finish_reason": "length",
                        "message": {"role": "assistant", "content": "", "tool_calls": []},
                    }
                ],
                "usage": {"prompt_tokens": 800, "completion_tokens": 1024},
            },
        )

    with pytest.raises(ContractViolation, match="exactly one tool call") as caught:
        asyncio.run(
            execute_one_request(
                NOTE,
                plan(),
                "test-secret",
                transport=httpx.MockTransport(handler),
            )
        )
    assert calls == 1
    assert caught.value.code == "output_budget_exhausted_before_tool_call"
    assert caught.value.diagnostics["finish_reason"] == "length"
    assert caught.value.diagnostics["completion_tokens_at_limit"] is True
    assert caught.value.diagnostics["assistant_content_present"] is False


def test_reasoning_only_failure_is_classified_without_retaining_reasoning_text():
    private_reasoning = "texto de razonamiento que no debe persistirse"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-reasoning-only",
                "choices": [
                    {
                        "finish_reason": "length",
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "reasoning_content": private_reasoning,
                            "tool_calls": [],
                        },
                    }
                ],
                "usage": {"prompt_tokens": 800, "completion_tokens": 1024},
            },
            headers={"x-request-id": "req-reasoning-only"},
        )

    with pytest.raises(ContractViolation) as caught:
        asyncio.run(
            execute_one_request(
                NOTE,
                plan(),
                "test-secret",
                transport=httpx.MockTransport(handler),
            )
        )

    assert caught.value.code == "reasoning_budget_exhausted_before_tool_call"
    assert caught.value.diagnostics["reasoning_content_present"] is True
    assert caught.value.diagnostics["reasoning_content_chars"] == len(private_reasoning)
    serialized = json.dumps(caught.value.diagnostics, ensure_ascii=False)
    assert private_reasoning not in serialized
    assert NOTE not in serialized
    assert "test-secret" not in serialized


def test_generated_quote_instead_of_source_is_rejected_without_retry():
    calls = 0
    arguments = valid_body()["choices"][0]["message"]["tool_calls"][0]["function"][
        "arguments"
    ]
    parsed_arguments = json.loads(arguments)
    parsed_arguments["evidence_sources"]["sample_points"] = ["12 puntos"]

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=valid_body(parsed_arguments))

    with pytest.raises(ContractViolation, match="invalid evidence source"):
        asyncio.run(
            execute_one_request(
                NOTE,
                plan(),
                "test-secret",
                transport=httpx.MockTransport(handler),
            )
        )
    assert calls == 1


def test_incomplete_tool_arguments_are_rejected_even_if_pydantic_has_defaults():
    arguments = json.loads(
        valid_body()["choices"][0]["message"]["tool_calls"][0]["function"][
            "arguments"
        ]
    )
    arguments.pop("note_sources")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=valid_body(arguments))

    with pytest.raises(ContractViolation, match="closed observation schema"):
        asyncio.run(
            execute_one_request(
                NOTE,
                plan(),
                "test-secret",
                transport=httpx.MockTransport(handler),
            )
        )


def test_nonliteral_notes_are_rejected_as_unsupported_claims():
    arguments = json.loads(
        valid_body()["choices"][0]["message"]["tool_calls"][0]["function"][
            "arguments"
        ]
    )
    arguments["note_sources"] = ["Aplicar fungicida mañana"]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=valid_body(arguments))

    with pytest.raises(ContractViolation, match="invalid note source"):
        asyncio.run(
            execute_one_request(
                NOTE,
                plan(),
                "test-secret",
                transport=httpx.MockTransport(handler),
            )
        )


def test_duplicate_uncertainties_are_rejected_client_side():
    arguments = json.loads(
        valid_body()["choices"][0]["message"]["tool_calls"][0]["function"][
            "arguments"
        ]
    )
    arguments["uncertainties"] = ["crop_stage", "crop_stage"]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=valid_body(arguments))

    with pytest.raises(ContractViolation, match="duplicate fields"):
        asyncio.run(
            execute_one_request(
                NOTE,
                plan(),
                "test-secret",
                transport=httpx.MockTransport(handler),
            )
        )


def test_missing_usage_is_not_counted_as_contract_pass():
    body = valid_body()
    body.pop("usage")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    with pytest.raises(ContractViolation, match="usage must include"):
        asyncio.run(
            execute_one_request(
                NOTE,
                plan(),
                "test-secret",
                transport=httpx.MockTransport(handler),
            )
        )


def test_upstream_http_failure_preserves_only_safe_metadata():
    private_body = "provider detail that must not escape"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422,
            json={"error": private_body},
            headers={"x-request-id": "req-safe-422"},
        )

    with pytest.raises(UpstreamRequestFailure) as caught:
        asyncio.run(
            execute_one_request(
                NOTE,
                plan(),
                "test-secret",
                transport=httpx.MockTransport(handler),
            )
        )

    assert str(caught.value) == (
        "Nebius returned HTTP 422; no automatic retry was attempted"
    )
    assert caught.value.code == "upstream_http_error"
    assert caught.value.diagnostics["http_status"] == 422
    assert caught.value.diagnostics["request_id"] == "req-safe-422"
    serialized = json.dumps(caught.value.diagnostics)
    assert private_body not in serialized
    assert NOTE not in serialized
    assert "test-secret" not in serialized


def test_free_text_alongside_tool_call_is_rejected():
    body = valid_body()
    body["choices"][0]["message"]["content"] = "Listo"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    with pytest.raises(ContractViolation, match="free text"):
        asyncio.run(
            execute_one_request(
                NOTE,
                plan(),
                "test-secret",
                transport=httpx.MockTransport(handler),
            )
        )


def test_default_settings_use_shared_token_factory_endpoint(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NEBIUS_BASE_URL", raising=False)
    settings = Settings.from_env()
    assert settings.nebius_base_url == DEFAULT_NEBIUS_BASE_URL


def test_application_local_provider_needs_no_live_authorization(tmp_path):
    provider = provider_for_application(make_settings(tmp_path))
    assert isinstance(provider, LocalExtractionProvider)


def test_application_nebius_provider_blocks_without_exact_confirmation(
    monkeypatch, tmp_path
):
    monkeypatch.delenv("AGROFIELD_NEBIUS_LIVE_CONFIRMATION", raising=False)
    with pytest.raises(PreflightBlocked, match="live request blocked"):
        provider_for_application(
            make_settings(tmp_path, provider="nebius", api_key="secret")
        )


def test_application_nebius_provider_requires_price_and_cap_env(monkeypatch, tmp_path):
    monkeypatch.setenv("AGROFIELD_NEBIUS_LIVE_CONFIRMATION", CONFIRMATION_PHRASE)
    monkeypatch.delenv("NEBIUS_INPUT_PRICE_PER_MILLION", raising=False)
    with pytest.raises(PreflightBlocked, match="NEBIUS_INPUT_PRICE_PER_MILLION"):
        provider_for_application(
            make_settings(tmp_path, provider="nebius", api_key="secret")
        )


def test_guarded_application_provider_allows_only_one_request(monkeypatch, tmp_path):
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=valid_body())

    monkeypatch.setenv("AGROFIELD_NEBIUS_LIVE_CONFIRMATION", CONFIRMATION_PHRASE)
    monkeypatch.setenv("NEBIUS_INPUT_PRICE_PER_MILLION", "0.06")
    monkeypatch.setenv("NEBIUS_OUTPUT_PRICE_PER_MILLION", "0.24")
    monkeypatch.setenv("NEBIUS_MAX_COST_USD", "0.01")
    provider = provider_for_application(
        make_settings(tmp_path, provider="nebius", api_key="test-secret"),
        transport=httpx.MockTransport(handler),
    )

    assert isinstance(provider, GuardedNebiusExtractionProvider)
    observation, telemetry = asyncio.run(provider.extract(NOTE))
    assert observation.crop_stage == "V3"
    assert telemetry.provider == "nebius"
    with pytest.raises(RuntimeError, match="one request per process"):
        asyncio.run(provider.extract(NOTE))
    assert calls == 1


def test_analyze_route_uses_guarded_nebius_contract_once(monkeypatch, tmp_path):
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=valid_body())

    guarded = GuardedNebiusExtractionProvider(
        plan=plan(),
        api_key="test-secret",
        transport=httpx.MockTransport(handler),
    )
    monkeypatch.setattr(app_module, "provider_for_application", lambda current: guarded)
    current_settings = make_settings(
        tmp_path, provider="nebius", api_key="test-secret"
    )
    repository = Repository(
        current_settings.database_path,
        PROJECT_ROOT / "fixtures" / "fields.json",
    )
    client = TestClient(app_module.create_app(current_settings, repository))

    first = client.post(
        "/api/analyze",
        json={"field_id": "lote-bajo", "raw_text": NOTE, "use_tavily": False},
    )
    second = client.post(
        "/api/analyze",
        json={"field_id": "lote-bajo", "raw_text": NOTE, "use_tavily": False},
    )

    assert first.status_code == 200
    assert first.json()["telemetry"]["provider"] == "nebius"
    assert second.status_code == 503
    assert "one request per process" in second.json()["detail"]
    assert calls == 1


def test_analyze_route_sanitizes_upstream_http_failure(monkeypatch, tmp_path):
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503, json={"error": "provider unavailable"})

    guarded = GuardedNebiusExtractionProvider(
        plan=plan(),
        api_key="test-secret",
        transport=httpx.MockTransport(handler),
    )
    monkeypatch.setattr(app_module, "provider_for_application", lambda current: guarded)
    current_settings = make_settings(
        tmp_path, provider="nebius", api_key="test-secret"
    )
    repository = Repository(
        current_settings.database_path,
        PROJECT_ROOT / "fixtures" / "fields.json",
    )
    client = TestClient(app_module.create_app(current_settings, repository))

    response = client.post(
        "/api/analyze",
        json={"field_id": "lote-bajo", "raw_text": NOTE, "use_tavily": False},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Nebius returned HTTP 503; no automatic retry was attempted"
    )
    assert "test-secret" not in response.text
    assert NOTE not in response.text
    assert calls == 1


@pytest.mark.parametrize(
    "field_name,sources,match",
    [
        ("event_type", ["inundación"], "invalid evidence source"),
        ("event_type", ["S99"], "invalid evidence source"),
        ("event_type", ["S04", "S04"], "invalid evidence source"),
        ("event_type", [], "missing evidence quote"),
        ("general_condition", ["S01"], "evidence quote supplied for an absent field"),
    ],
)
def test_evidence_source_failures_keep_diagnostics_without_accepting_an_observation(
    field_name, sources, match,
):
    arguments = json.loads(valid_body()["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])
    arguments["evidence_sources"][field_name] = sources
    with pytest.raises(ContractViolation, match=match) as caught:
        asyncio.run(execute_one_request(
            NOTE, plan(), "test-secret",
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json=valid_body(arguments))),
        ))
    assert caught.value.diagnostics["http_status"] == 200
    assert caught.value.diagnostics["tool_call_count"] == 1
    assert caught.value.diagnostics["prompt_tokens"] == 900
    assert NOTE not in json.dumps(caught.value.diagnostics)
    assert "inundación" not in str(caught.value)


def test_literal_guard_still_rejects_translations_and_even_changed_case():
    for quote in ("inundación", "Agua parada"):
        draft = ObservationDraft(event_type="flooding", evidence_quotes={"event_type": quote})
        with pytest.raises(ContractViolation, match="non-literal evidence"):
            _validate_evidence(draft, NOTE)


def test_route_contract_failure_preserves_safe_diagnostics_and_creates_no_tasks(monkeypatch, tmp_path):
    calls = 0
    arguments = json.loads(valid_body()["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])
    arguments["evidence_sources"]["event_type"] = ["invented private quotation"]

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=valid_body(arguments), headers={"x-request-id": "req-contract"})

    guarded = GuardedNebiusExtractionProvider(plan(), "test-secret", httpx.MockTransport(handler))
    monkeypatch.setattr(app_module, "provider_for_application", lambda current: guarded)
    current_settings = make_settings(tmp_path, provider="nebius", api_key="test-secret")
    repository = Repository(current_settings.database_path, PROJECT_ROOT / "fixtures" / "fields.json")
    client = TestClient(app_module.create_app(current_settings, repository))
    before = client.get("/api/audit").json()
    response = client.post("/api/analyze", json={"field_id": "lote-bajo", "raw_text": NOTE})
    assert response.status_code == 503
    assert response.json()["failure_code"] == "invalid_evidence_source"
    assert response.json()["safe_diagnostics"]["request_id"] == "req-contract"
    assert response.json()["safe_diagnostics"]["http_status"] == 200
    assert response.json()["automatic_retry"] is False
    assert all(value not in response.text for value in (NOTE, "test-secret", "invented private quotation"))
    assert client.get("/api/audit").json() == before
    second = client.post("/api/analyze", json={"field_id": "lote-bajo", "raw_text": NOTE})
    assert second.status_code == 503
    assert "one request per process" in second.json()["detail"]
    assert calls == 1


def test_malformed_response_metadata_is_sanitized_instead_of_crashing():
    body = valid_body()
    body["id"] = "private@example.invalid"
    body["choices"][0]["finish_reason"] = {"private": "text"}
    body["choices"][0]["message"] = []
    with pytest.raises(ContractViolation) as caught:
        asyncio.run(execute_one_request(
            NOTE, plan(), "test-secret",
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body)),
        ))
    assert caught.value.diagnostics["request_id"] is None
    assert caught.value.diagnostics["finish_reason"] is None
    assert "private" not in json.dumps(caught.value.diagnostics)


@pytest.mark.parametrize("field_name,value", [
    ("event_hours_ago", -1),
    ("event_hours_ago", float("nan")),
    ("event_hours_ago", float("inf")),
    ("sample_points", -1),
    ("water_duration_hours", float("inf")),
    ("stand_count_per_m", float("inf")),
])
def test_invalid_quantities_fail_closed_without_retry_or_local_fallback(field_name, value, monkeypatch):
    arguments = json.loads(valid_body()["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])
    arguments[field_name] = value
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=valid_body(arguments))

    async def forbidden_fallback(*args, **kwargs):
        pytest.fail("Rejected model data must not be filled by the local provider")

    monkeypatch.setattr(LocalExtractionProvider, "extract", forbidden_fallback)
    provider = GuardedNebiusExtractionProvider(plan(), "test-secret", httpx.MockTransport(handler))
    with pytest.raises(ContractViolation) as caught:
        asyncio.run(provider.extract(NOTE))
    assert caught.value.code == "invalid_measurement"
    assert caught.value.diagnostics["http_status"] == 200
    assert NOTE not in str(caught.value)
    assert "test-secret" not in str(caught.value)
    with pytest.raises(RuntimeError, match="one request per process"):
        asyncio.run(provider.extract(NOTE))
    assert calls == 1
