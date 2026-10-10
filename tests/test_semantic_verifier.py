import asyncio
import json
from decimal import Decimal

import httpx
import pytest

from agrofield_agent.app import PROJECT_ROOT
from agrofield_agent.config import DEFAULT_NEBIUS_BASE_URL
from agrofield_agent.models import ObservationDraft, ProviderTelemetry
from agrofield_agent.nebius_smoke import SmokePlan
from agrofield_agent.semantic_verifier import (
    VERIFIER_TOOL_NAME,
    VerifiedExtractionProvider,
    apply_verdicts,
    asserted_fields,
    build_verification_payload,
    verification_context,
    verify_observation,
)


NOTE = (PROJECT_ROOT / "fixtures" / "nebius_smoke_note.txt").read_text(encoding="utf-8").strip()
SECRET = "verifier-test-secret-not-a-credential"


def plan():
    return SmokePlan(
        model="nvidia/nemotron-3-super-120b-a12b", base_url=DEFAULT_NEBIUS_BASE_URL,
        max_completion_tokens=1024, prompt_token_budget=16384,
        input_price_per_million=Decimal("0.3"), output_price_per_million=Decimal("0.9"),
        max_cost_usd=Decimal("0.01"),
    )


def draft():
    return ObservationDraft(
        crop_stage="V3", event_type="flooding", event_hours_ago=18, access_safe=True,
        sample_points=6, affected_area_pct=35, standing_water_pct=35,
        water_duration_hours=14, general_condition="mixed",
        evidence_quotes={
            "crop_stage": "Soja V3.", "event_type": "El agua parada afecta 35% del lote desde hace 14 horas.",
            "event_hours_ago": "Tormenta hace 18 horas, acceso seguro.",
            "access_safe": "Tormenta hace 18 horas, acceso seguro.",
            "sample_points": "Recorrí 6 puntos.",
            "affected_area_pct": "El agua parada afecta 35% del lote desde hace 14 horas.",
            "standing_water_pct": "El agua parada afecta 35% del lote desde hace 14 horas.",
            "water_duration_hours": "El agua parada afecta 35% del lote desde hace 14 horas.",
            "general_condition": "Tormenta hace 18 horas, acceso seguro.",
        },
    )


def body(verdicts, *, name=VERIFIER_TOOL_NAME, content=None, usage=True):
    message = {"role": "assistant", "content": content, "tool_calls": [{
        "id": "call", "type": "function",
        "function": {"name": name, "arguments": json.dumps(verdicts)},
    }]}
    payload = {"id": "chatcmpl-verify", "choices": [{"finish_reason": "tool_calls", "message": message}]}
    if usage:
        payload["usage"] = {"prompt_tokens": 1200, "completion_tokens": 80}
    return payload


def all_supported(except_for=()):
    return {name: ("unsupported" if name in except_for else "supported")
            for name in asserted_fields(draft())}


def test_payload_lists_every_asserted_claim_with_its_definition_and_quote():
    payload = build_verification_payload(NOTE, draft(), plan())
    user = json.loads(payload["messages"][1]["content"])
    assert [claim["field"] for claim in user["claims"]] == asserted_fields(draft())
    assert user["claims"][-1] == {
        "field": "general_condition", "value": "mixed",
        "definition": payload and user["claims"][-1]["definition"],
        "quote": "Tormenta hace 18 horas, acceso seguro.",
    }
    assert "NO establecen condición" in user["claims"][-1]["definition"]
    schema = payload["tools"][0]["function"]["parameters"]
    assert schema["required"] == asserted_fields(draft())
    assert schema["additionalProperties"] is False
    assert payload["tool_choice"]["function"]["name"] == VERIFIER_TOOL_NAME
    assert payload["chat_template_kwargs"] == {"enable_thinking": False}


def test_unsupported_verdict_clears_the_field_and_adds_an_uncertainty():
    cleared = apply_verdicts(draft(), all_supported(except_for=("general_condition", "sample_points")))
    assert cleared.general_condition == "unknown"
    assert cleared.sample_points is None
    assert cleared.evidence_quotes["general_condition"] == ""
    assert cleared.evidence_quotes["sample_points"] == ""
    assert cleared.uncertainties == ["sample_points", "general_condition"]
    assert cleared.crop_stage == "V3" and cleared.evidence_quotes["crop_stage"] == "Soja V3."
    assert apply_verdicts(draft(), all_supported()) == draft()


def test_live_verdicts_are_applied_and_reported_without_the_key():
    seen = {}

    def endpoint(request):
        seen["auth"] = request.headers["Authorization"]
        seen["model"] = json.loads(request.content)["model"]
        return httpx.Response(200, json=body(all_supported(except_for=("general_condition",))),
                              headers={"x-request-id": "req-verify-1"})

    verified, report = asyncio.run(verify_observation(
        NOTE, draft(), plan(), SECRET, transport=httpx.MockTransport(endpoint)
    ))

    assert seen == {"auth": f"Bearer {SECRET}", "model": plan().model}
    assert verified.general_condition == "unknown"
    assert report["status"] == "verified"
    assert report["cleared"] == ["general_condition"]
    assert len(report["supported"]) == 8
    assert report["telemetry"]["request_id"] == "req-verify-1"
    assert report["telemetry"]["estimated_cost_usd"] == "0.00043200"
    assert SECRET not in json.dumps(report)


@pytest.mark.parametrize("response", [
    lambda: httpx.Response(200, json=body({**all_supported(), "extra": "supported"})),
    lambda: httpx.Response(200, json=body({name: "maybe" for name in asserted_fields(draft())})),
    lambda: httpx.Response(200, json=body(all_supported(), name="other_tool")),
    lambda: httpx.Response(200, json=body(all_supported(), content="texto libre")),
    lambda: httpx.Response(200, json=body(all_supported(), usage=False)),
    lambda: httpx.Response(503, json={"error": "synthetic"}),
    lambda: httpx.Response(200, content=b"not json"),
])
def test_any_failure_leaves_the_draft_unchanged_and_unverified(response):
    calls = 0

    def endpoint(request):
        nonlocal calls
        calls += 1
        return response()

    verified, report = asyncio.run(verify_observation(
        NOTE, draft(), plan(), SECRET, transport=httpx.MockTransport(endpoint)
    ))

    assert calls == 1
    assert verified == draft()
    assert report["status"] == "unverified" and report["cleared"] == []
    assert report["automatic_retry"] is False
    assert SECRET not in json.dumps(report) and NOTE not in json.dumps(report)


def test_nothing_to_verify_sends_no_request():
    empty = ObservationDraft()
    verified, report = asyncio.run(verify_observation(
        NOTE, empty, plan(), SECRET,
        transport=httpx.MockTransport(lambda request: pytest.fail("no request expected")),
    ))
    assert verified == empty and report["status"] == "nothing_to_verify"


def test_provider_wrapper_publishes_the_report_in_the_task_context_and_settles_admission():
    class Inner:
        async def extract(self, raw_text):
            return draft(), ProviderTelemetry(provider="nebius", model="nano", latency_ms=1.0)

    settled = []

    def admit(ceiling):
        assert ceiling == Decimal("0.00583680")
        return lambda status, cost: settled.append((status, cost))

    provider = VerifiedExtractionProvider(
        inner=Inner(), plan=plan(), api_key=SECRET,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=body(all_supported(except_for=("sample_points",))),
                                           headers={"x-request-id": "req-2"})
        ),
        admit=admit,
    )

    async def run():
        verification_context.set(None)
        observation, telemetry = await provider.extract(NOTE)
        return observation, telemetry, verification_context.get()

    observation, telemetry, report = asyncio.run(run())
    assert observation.sample_points is None and telemetry.provider == "nebius"
    assert report["cleared"] == ["sample_points"]
    assert settled == [("accepted", Decimal("0.00043200"))]
    assert SECRET not in repr(provider)
