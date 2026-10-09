import asyncio
import json
from decimal import Decimal

import httpx
import pytest
from fastapi.testclient import TestClient

import agrofield_agent.app as app_module
from agrofield_agent.app import PROJECT_ROOT
from agrofield_agent.config import DEFAULT_NEBIUS_BASE_URL, Settings
from agrofield_agent.demo_provider import (
    DEMO_CONFIRMATION_PHRASE,
    DEMO_PROVIDER,
    BudgetedNebiusExtractionProvider,
    DemoLimitReached,
    DemoLimits,
    SpendLedger,
    demo_provider_from_env,
)
from agrofield_agent.handoff_runner import simulated_arguments
from agrofield_agent.nebius_smoke import (
    DEFAULT_MODEL,
    ContractViolation,
    PreflightBlocked,
    SmokePlan,
    UpstreamRequestFailure,
)
from agrofield_agent.repository import Repository


NOTE = (PROJECT_ROOT / "fixtures" / "nebius_smoke_note.txt").read_text(encoding="utf-8").strip()
SECRET = "demo-test-secret-not-a-credential"
CEILING = Decimal("0.00122880")
ACCEPTED_COST = Decimal("0.00008280")


def plan():
    return SmokePlan(
        model=DEFAULT_MODEL, base_url=DEFAULT_NEBIUS_BASE_URL,
        max_completion_tokens=1024, prompt_token_budget=16384,
        input_price_per_million=Decimal("0.06"),
        output_price_per_million=Decimal("0.24"), max_cost_usd=Decimal("0.01"),
    )


def body(arguments=None):
    return {
        "id": "chatcmpl-demo-test",
        "choices": [{
            "finish_reason": "tool_calls",
            "message": {"role": "assistant", "content": None, "tool_calls": [{
                "id": "call", "type": "function",
                "function": {"name": "record_field_observation",
                             "arguments": json.dumps(arguments or simulated_arguments())},
            }]},
        }],
        "usage": {"prompt_tokens": 900, "completion_tokens": 120},
    }


class Endpoint:
    def __init__(self, response=None):
        self.calls = 0
        self.response = response or (lambda: httpx.Response(200, json=body()))

    def __call__(self, request):
        self.calls += 1
        return self.response()


def make_provider(tmp_path, endpoint, clock=None, **limits):
    values = {"total_budget_usd": Decimal("1"), "daily_requests": 100,
              "requests_per_minute": 60}
    values.update(limits)
    return BudgetedNebiusExtractionProvider(
        plan=plan(), api_key=SECRET,
        ledger=SpendLedger(tmp_path / "ledger.sqlite3", clock or (lambda: 1_800_000_000.0)),
        limits=DemoLimits(**values), transport=httpx.MockTransport(endpoint),
    )


def test_many_notes_are_served_and_settled_at_reported_usage(tmp_path):
    endpoint = Endpoint()
    provider = make_provider(tmp_path, endpoint)

    for _ in range(3):
        draft, telemetry = asyncio.run(provider.extract(NOTE))

    assert draft.crop_stage == "V3" and telemetry.provider == "nebius"
    assert endpoint.calls == 3
    budget = provider.budget()
    assert budget["requests_total"] == budget["requests_accepted"] == 3
    assert Decimal(budget["estimated_spend_usd"]) == 3 * ACCEPTED_COST
    assert budget["automatic_retries"] == 0
    assert SECRET not in json.dumps(budget) + repr(provider)


def test_total_budget_blocks_before_network_and_survives_a_restart(tmp_path):
    endpoint = Endpoint()
    # Room for exactly one reserved ceiling.
    provider = make_provider(tmp_path, endpoint, total_budget_usd=CEILING + ACCEPTED_COST / 2)
    asyncio.run(provider.extract(NOTE))

    restarted = make_provider(tmp_path, endpoint, total_budget_usd=CEILING + ACCEPTED_COST / 2)
    with pytest.raises(DemoLimitReached) as error:
        asyncio.run(restarted.extract(NOTE))

    assert error.value.code == "demo_budget_exhausted"
    assert endpoint.calls == 1
    assert restarted.budget()["requests_total"] == 1


def test_daily_cap_resets_on_the_next_utc_day(tmp_path):
    endpoint, now = Endpoint(), [1_800_000_000.0]
    provider = make_provider(tmp_path, endpoint, lambda: now[0], daily_requests=2)
    asyncio.run(provider.extract(NOTE))
    asyncio.run(provider.extract(NOTE))
    with pytest.raises(DemoLimitReached) as error:
        asyncio.run(provider.extract(NOTE))
    assert error.value.code == "demo_daily_cap_reached"

    now[0] += 86_400
    asyncio.run(provider.extract(NOTE))
    assert endpoint.calls == 3


def test_rate_limit_blocks_bursts_before_network(tmp_path):
    endpoint, now = Endpoint(), [1_800_000_000.0]
    provider = make_provider(tmp_path, endpoint, lambda: now[0], requests_per_minute=1)
    asyncio.run(provider.extract(NOTE))
    with pytest.raises(DemoLimitReached) as error:
        asyncio.run(provider.extract(NOTE))
    assert error.value.code == "demo_rate_limited"

    now[0] += 61
    asyncio.run(provider.extract(NOTE))
    assert endpoint.calls == 2


def test_upstream_failure_is_not_retried_and_keeps_the_reserved_ceiling(tmp_path):
    endpoint = Endpoint(lambda: httpx.Response(500, json={"error": "synthetic"}))
    provider = make_provider(tmp_path, endpoint)

    with pytest.raises(UpstreamRequestFailure):
        asyncio.run(provider.extract(NOTE))

    assert endpoint.calls == 1
    budget = provider.budget()
    assert budget["requests_accepted"] == 0
    assert Decimal(budget["estimated_spend_usd"]) == CEILING


def test_contract_rejection_is_charged_at_reported_usage_without_local_fallback(tmp_path):
    arguments = simulated_arguments()
    arguments["evidence_sources"]["crop_stage"] = ["S99"]
    endpoint = Endpoint(lambda: httpx.Response(200, json=body(arguments)))
    provider = make_provider(tmp_path, endpoint)

    with pytest.raises(ContractViolation):
        asyncio.run(provider.extract(NOTE))

    budget = provider.budget()
    assert endpoint.calls == 1 and budget["requests_accepted"] == 0
    assert Decimal(budget["estimated_spend_usd"]) == ACCEPTED_COST


def settings_for(tmp_path, provider=DEMO_PROVIDER, key=SECRET):
    return Settings(
        provider=provider, database_path=tmp_path / "app.sqlite3", nebius_api_key=key,
        nebius_base_url=DEFAULT_NEBIUS_BASE_URL, nebius_model=DEFAULT_MODEL,
        tavily_api_key=None, tavily_include_domains=(),
    )


def demo_env(monkeypatch, **changes):
    values = {
        "AGROFIELD_NEBIUS_DEMO_CONFIRMATION": DEMO_CONFIRMATION_PHRASE,
        "NEBIUS_INPUT_PRICE_PER_MILLION": "0.06",
        "NEBIUS_OUTPUT_PRICE_PER_MILLION": "0.24",
        "NEBIUS_MAX_COST_USD": "0.01",
        "AGROFIELD_DEMO_TOTAL_BUDGET_USD": "1",
    }
    values.update(changes)
    for name in ("NEBIUS_REASONING_EFFORT", "AGROFIELD_DEMO_LEDGER_PATH",
                 "AGROFIELD_DEMO_DAILY_REQUESTS", "AGROFIELD_DEMO_REQUESTS_PER_MINUTE"):
        monkeypatch.delenv(name, raising=False)
    for name, value in values.items():
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)


@pytest.mark.parametrize("changes,key", [
    ({"AGROFIELD_NEBIUS_DEMO_CONFIRMATION": None}, SECRET),
    ({"AGROFIELD_NEBIUS_DEMO_CONFIRMATION": "RUN_ONE_NEBIUS_REQUEST"}, SECRET),
    ({"AGROFIELD_DEMO_TOTAL_BUDGET_USD": None}, SECRET),
    ({"AGROFIELD_DEMO_TOTAL_BUDGET_USD": "0"}, SECRET),
    ({"NEBIUS_INPUT_PRICE_PER_MILLION": None}, SECRET),
    ({"NEBIUS_MAX_COST_USD": None}, SECRET),
    ({"AGROFIELD_DEMO_DAILY_REQUESTS": "0"}, SECRET),
    ({"NEBIUS_REASONING_EFFORT": "low"}, SECRET),
    ({}, None),
])
def test_demo_mode_refuses_to_start_without_every_guard(monkeypatch, tmp_path, changes, key):
    demo_env(monkeypatch, **changes)
    with pytest.raises(PreflightBlocked):
        demo_provider_from_env(settings_for(tmp_path, key=key))
    with pytest.raises(PreflightBlocked):
        app_module.create_app(settings_for(tmp_path, key=key))


def demo_client(monkeypatch, tmp_path, endpoint, **env):
    demo_env(monkeypatch, **env)
    settings = settings_for(tmp_path)
    provider = demo_provider_from_env(settings, transport=httpx.MockTransport(endpoint))
    repository = Repository(settings.database_path, PROJECT_ROOT / "fixtures" / "fields.json")
    return TestClient(app_module.create_app(settings, repository, provider))


def test_public_route_serves_repeated_nemotron_analyses_and_reports_budget(
    monkeypatch, tmp_path
):
    endpoint = Endpoint()
    client = demo_client(monkeypatch, tmp_path, endpoint)
    request = {"field_id": "lote-bajo", "raw_text": NOTE, "use_tavily": False}

    responses = [client.post("/api/analyze", json=request) for _ in range(2)]
    runtime = client.get("/api/runtime")

    assert [item.status_code for item in responses] == [200, 200]
    assert responses[1].json()["telemetry"]["provider"] == "nebius"
    assert endpoint.calls == 2
    assert runtime.json()["nemotron_runtime"] is True
    assert runtime.json()["demo_budget"]["requests_accepted"] == 2
    assert (tmp_path / "nebius-demo-ledger.sqlite3").exists()
    assert SECRET not in runtime.text + responses[0].text + client.get("/health").text


def test_exhausted_budget_returns_429_and_only_an_explicit_local_engine_answers(
    monkeypatch, tmp_path
):
    endpoint = Endpoint()
    client = demo_client(
        monkeypatch, tmp_path, endpoint, AGROFIELD_DEMO_TOTAL_BUDGET_USD="0.001"
    )
    request = {"field_id": "lote-bajo", "raw_text": NOTE, "use_tavily": False}

    blocked = client.post("/api/analyze", json=request)
    local = client.post("/api/analyze?engine=local", json=request)

    assert blocked.status_code == 429
    assert blocked.json()["failure_code"] == "demo_budget_exhausted"
    assert blocked.json()["local_engine_available"] is True
    assert endpoint.calls == 0
    assert local.status_code == 200
    assert local.json()["telemetry"] == {
        **local.json()["telemetry"], "provider": "local", "model": "deterministic-es-v0.1",
    }
    assert local.json()["observation"]["provider"] == "local"


def test_local_default_runtime_reports_no_nemotron_and_no_budget(tmp_path):
    settings = settings_for(tmp_path, provider="local", key=None)
    repository = Repository(settings.database_path, PROJECT_ROOT / "fixtures" / "fields.json")
    runtime = TestClient(app_module.create_app(settings, repository)).get("/api/runtime")

    assert runtime.json() == {
        "provider": "local", "model": "deterministic-es-v0.1",
        "nemotron_runtime": False, "demo_budget": None,
    }
