import asyncio
import json
from decimal import Decimal

import httpx
import pytest

from agrofield_agent.config import DEFAULT_NEBIUS_BASE_URL, Settings
from agrofield_agent.nebius_smoke import (
    CONFIRMATION_PHRASE,
    ContractViolation,
    PreflightBlocked,
    SmokePlan,
    execute_one_request,
    preflight,
    require_live_confirmation,
)


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
        "reasoning_effort": "low",
    }
    values.update(changes)
    return SmokePlan(**values)


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
        "evidence_quotes": {
            "crop_stage": "Soja V3",
            "event_type": "agua parada",
            "event_hours_ago": "hace 18 horas",
            "access_safe": "acceso seguro",
            "sample_points": "6 puntos",
            "affected_area_pct": "afecta 35% del lote",
            "standing_water_pct": "agua parada afecta 35% del lote",
            "water_duration_hours": "desde hace 14 horas",
        },
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
    assert payload["reasoning_effort"] == "low"
    assert payload["n"] == 1
    assert payload["stream"] is False
    assert payload["store"] is False
    assert payload["tool_choice"]["function"]["name"] == "record_field_observation"
    assert payload["tools"][0]["function"]["strict"] is True


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

    with pytest.raises(ContractViolation, match="exactly one tool call"):
        asyncio.run(
            execute_one_request(
                NOTE,
                plan(),
                "test-secret",
                transport=httpx.MockTransport(handler),
            )
        )
    assert calls == 1


def test_nonliteral_evidence_is_rejected_without_retry():
    calls = 0
    arguments = valid_body()["choices"][0]["message"]["tool_calls"][0]["function"][
        "arguments"
    ]
    parsed_arguments = json.loads(arguments)
    parsed_arguments["evidence_quotes"]["sample_points"] = "12 puntos"

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=valid_body(parsed_arguments))

    with pytest.raises(ContractViolation, match="non-literal evidence"):
        asyncio.run(
            execute_one_request(
                NOTE,
                plan(),
                "test-secret",
                transport=httpx.MockTransport(handler),
            )
        )
    assert calls == 1


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
