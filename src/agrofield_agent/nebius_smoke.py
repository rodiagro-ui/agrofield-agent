from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import time
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal
from urllib.parse import urlparse

import httpx
from pydantic import ValidationError

from agrofield_agent.config import DEFAULT_NEBIUS_BASE_URL, Settings
from agrofield_agent.evidence import resolve_sources, source_catalog
from agrofield_agent.extraction_contract import (
    EVIDENCE_FIELDS, FIELD_DESCRIPTIONS, PROFILE_ID, SYSTEM_PROMPT, TOOL_NAME,
)
from agrofield_agent.models import ObservationDraft, ProviderTelemetry

if TYPE_CHECKING:
    from agrofield_agent.services.extraction import ExtractionProvider


CONFIRMATION_PHRASE = "RUN_ONE_NEBIUS_REQUEST"
DEFAULT_MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"
PROMPT_OVERHEAD_TOKEN_MARGIN = 1024
MONEY_QUANTUM = Decimal("0.00000001")

class SmokeHarnessError(RuntimeError):
    """Base error for a request that must not be retried automatically."""


class PreflightBlocked(SmokeHarnessError):
    """The request is blocked before network access."""


class ContractViolation(SmokeHarnessError):
    """Nebius answered, but the structured evidence contract was not satisfied."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "contract_violation",
        diagnostics: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.diagnostics = diagnostics or {}


class UpstreamRequestFailure(SmokeHarnessError):
    """A sanitized HTTP/transport failure from the inference endpoint."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        diagnostics: dict[str, Any],
    ) -> None:
        super().__init__(message)
        self.code = code
        self.diagnostics = diagnostics


@dataclass(frozen=True)
class SmokePlan:
    model: str
    base_url: str
    max_completion_tokens: int
    prompt_token_budget: int
    input_price_per_million: Decimal
    output_price_per_million: Decimal
    max_cost_usd: Decimal
    reasoning_effort: Literal[
        "none", "minimal", "low", "medium", "high", "xhigh"
    ] = "none"
    timeout_seconds: float = 45.0


@dataclass(frozen=True)
class CostPreflight:
    serialized_request_bytes: int
    prompt_token_ceiling: int
    completion_token_ceiling: int
    estimated_cost_ceiling_usd: Decimal

    def public_dict(self) -> dict[str, Any]:
        return {
            "serialized_request_bytes": self.serialized_request_bytes,
            "prompt_token_ceiling": self.prompt_token_ceiling,
            "completion_token_ceiling": self.completion_token_ceiling,
            "estimated_cost_ceiling_usd": _money(self.estimated_cost_ceiling_usd),
        }


def _money(value: Decimal) -> str:
    return format(value.quantize(MONEY_QUANTUM, rounding=ROUND_CEILING), "f")


def _validate_plan(plan: SmokePlan) -> None:
    parsed = urlparse(plan.base_url)
    hostname = (parsed.hostname or "").lower()
    is_nebius_api = hostname == "api.tokenfactory.nebius.com" or (
        hostname.startswith("api.tokenfactory.") and hostname.endswith(".nebius.com")
    )
    if parsed.scheme != "https" or not is_nebius_api:
        raise PreflightBlocked("NEBIUS_BASE_URL must be an HTTPS Token Factory host")
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise PreflightBlocked("NEBIUS_BASE_URL cannot contain credentials, query, or fragment")
    if not parsed.path.rstrip("/").endswith("/v1"):
        raise PreflightBlocked("NEBIUS_BASE_URL must end in /v1")
    if not plan.model.strip():
        raise PreflightBlocked("model is required")
    if plan.max_completion_tokens < 256 or plan.max_completion_tokens > 4096:
        raise PreflightBlocked("max_completion_tokens must be between 256 and 4096")
    if plan.prompt_token_budget < 2048 or plan.prompt_token_budget > 131072:
        raise PreflightBlocked("prompt_token_budget must be between 2048 and 131072")
    if plan.input_price_per_million <= 0 or plan.output_price_per_million <= 0:
        raise PreflightBlocked("pricing inputs must be positive")
    if plan.max_cost_usd <= 0:
        raise PreflightBlocked("max_cost_usd must be positive")
    if plan.timeout_seconds <= 0 or plan.timeout_seconds > 60:
        raise PreflightBlocked("timeout_seconds must be in (0, 60]")
    if plan.model == DEFAULT_MODEL and plan.reasoning_effort != "none":
        raise PreflightBlocked(
            "the guarded Nemotron profile requires reasoning_effort=none"
        )


def strict_observation_schema(raw_text: str) -> dict[str, Any]:
    """Return a small strict schema with explicit representations for missing data."""

    def nullable(value_schema: dict[str, Any]) -> dict[str, Any]:
        return {"anyOf": [value_schema, {"type": "null"}]}

    def percentage() -> dict[str, Any]:
        return nullable({"type": "number", "minimum": 0, "maximum": 100})
    def source_list() -> dict[str, Any]:
        return {
            "type": "array",
            "items": {"type": "string", "enum": list(source_catalog(raw_text))},
            "description": "IDs que respaldan el hecho; [] si no fue observado.",
        }

    evidence_properties = {field_name: source_list() for field_name in EVIDENCE_FIELDS}
    properties: dict[str, Any] = {
        "crop_stage": nullable(
            {
                "type": "string",
                "description": "Etapa fenológica explícita tal como figura en la nota.",
            }
        ),
        "event_type": {
            "type": "string",
            "enum": ["flooding", "hail", "wind", "mixed", "none", "unknown"],
        },
        "event_hours_ago": nullable({"type": "number", "minimum": 0}),
        "access_safe": nullable({"type": "boolean"}),
        "sample_points": nullable({"type": "integer", "minimum": 0}),
        "affected_area_pct": percentage(),
        "standing_water_pct": percentage(),
        "water_duration_hours": nullable({"type": "number", "minimum": 0}),
        "lodging_pct": percentage(),
        "stem_damage_pct": percentage(),
        "stand_count_per_m": nullable({"type": "number", "minimum": 0}),
        "general_condition": {
            "type": "string",
            "enum": ["critical", "poor", "mixed", "good", "unknown"],
        },
        "note_sources": source_list(),
        "evidence_sources": {
            "type": "object",
            "properties": evidence_properties,
            "required": list(EVIDENCE_FIELDS),
            "additionalProperties": False,
        },
        "uncertainties": {
            "type": "array",
            "items": {"type": "string", "enum": list(EVIDENCE_FIELDS)},
            "description": "Campos cuya evidencia es ambigua; no inferencias agronómicas.",
        },
    }
    for field_name, description in FIELD_DESCRIPTIONS.items():
        properties[field_name]["description"] = description
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def build_payload(raw_text: str, plan: SmokePlan) -> dict[str, Any]:
    note = raw_text.strip()
    if len(note) < 5 or len(note) > 8000:
        raise PreflightBlocked("synthetic note length must be between 5 and 8000 characters")
    schema = strict_observation_schema(raw_text)
    return {
        "model": plan.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps({"sources": source_catalog(raw_text)}, ensure_ascii=False),
            },
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": TOOL_NAME,
                    "description": "Registra únicamente hechos explícitos de la nota de campo.",
                    "parameters": schema,
                    "strict": True,
                },
            }
        ],
        "tool_choice": {
            "type": "function",
            "function": {"name": TOOL_NAME},
        },
        "temperature": 0,
        "reasoning_effort": plan.reasoning_effort,
        # `extra_body` is an OpenAI SDK option that merges vendor-specific
        # parameters into the HTTP body. This module posts raw JSON with httpx,
        # so the vLLM parameter itself must be top-level.
        "chat_template_kwargs": {"enable_thinking": False},
        "max_completion_tokens": plan.max_completion_tokens,
        "n": 1,
        "stream": False,
        "store": False,
    }


def preflight(raw_text: str, plan: SmokePlan) -> tuple[dict[str, Any], CostPreflight]:
    _validate_plan(plan)
    payload = build_payload(raw_text, plan)
    serialized_bytes = len(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )
    conservative_prompt_proxy = serialized_bytes + PROMPT_OVERHEAD_TOKEN_MARGIN
    if conservative_prompt_proxy > plan.prompt_token_budget:
        raise PreflightBlocked(
            "serialized request plus safety margin exceeds prompt_token_budget"
        )
    cost_ceiling = (
        Decimal(plan.prompt_token_budget) * plan.input_price_per_million
        + Decimal(plan.max_completion_tokens) * plan.output_price_per_million
    ) / Decimal(1_000_000)
    estimate = CostPreflight(
        serialized_request_bytes=serialized_bytes,
        prompt_token_ceiling=plan.prompt_token_budget,
        completion_token_ceiling=plan.max_completion_tokens,
        estimated_cost_ceiling_usd=cost_ceiling,
    )
    if cost_ceiling > plan.max_cost_usd:
        raise PreflightBlocked(
            f"estimated cost ceiling {_money(cost_ceiling)} exceeds authorized cap "
            f"{_money(plan.max_cost_usd)}"
        )
    return payload, estimate


def require_live_confirmation(value: str | None) -> None:
    if value != CONFIRMATION_PHRASE:
        raise PreflightBlocked(
            f"live request blocked; pass --confirm-live {CONFIRMATION_PHRASE} only after "
            "fresh human authorization"
        )


def _validate_evidence(draft: ObservationDraft, raw_text: str) -> None:
    unknown_keys = sorted(set(draft.evidence_quotes) - set(EVIDENCE_FIELDS))
    if unknown_keys:
        raise ContractViolation(
            "evidence_quotes contains unsupported keys: " + ", ".join(unknown_keys)
        )
    missing: list[str] = []
    nonliteral: list[str] = []
    unexpected: list[str] = []
    values = draft.model_dump()
    for field in EVIDENCE_FIELDS:
        value = values[field]
        quote = draft.evidence_quotes.get(field, "").strip()
        if value is None or value == "unknown":
            if quote:
                unexpected.append(field)
            continue
        if not quote:
            missing.append(field)
        elif quote not in raw_text:
            nonliteral.append(field)
    if missing:
        raise ContractViolation("missing evidence quote for: " + ", ".join(missing))
    if nonliteral:
        raise ContractViolation("non-literal evidence quote for: " + ", ".join(nonliteral))
    if unexpected:
        raise ContractViolation(
            "evidence quote supplied for an absent field: " + ", ".join(unexpected)
        )
    unsupported_uncertainties = sorted(set(draft.uncertainties) - set(EVIDENCE_FIELDS))
    if unsupported_uncertainties:
        raise ContractViolation(
            "uncertainties contains unsupported fields: "
            + ", ".join(unsupported_uncertainties)
        )
    if len(draft.uncertainties) != len(set(draft.uncertainties)):
        raise ContractViolation("uncertainties contains duplicate fields")
    nonliteral_notes = [
        str(index)
        for index, item in enumerate(draft.notes)
        if not item.strip() or item not in raw_text
    ]
    if nonliteral_notes:
        raise ContractViolation(
            "notes must be non-empty literal fragments; invalid indexes: "
            + ", ".join(nonliteral_notes)
        )


def _validate_quantities(draft: ObservationDraft) -> None:
    """Enforce wire-schema minima even where the shared model lacks them."""
    for field_name in (
        "event_hours_ago", "sample_points", "affected_area_pct", "standing_water_pct",
        "water_duration_hours", "lodging_pct", "stem_damage_pct", "stand_count_per_m",
    ):
        value = getattr(draft, field_name)
        if value is not None and (
            value < 0 or (isinstance(value, float) and not math.isfinite(value))
        ):
            raise ContractViolation(
                f"invalid nonnegative finite measurement for: {field_name}",
                code="invalid_measurement",
            )


def _resolve_arguments(parsed_arguments: dict[str, Any], raw_text: str) -> dict[str, Any]:
    schema = strict_observation_schema(raw_text)
    expected_fields = set(schema["properties"])
    # v3: a model that omits an empty list has not asserted anything, so the
    # omission is filled with []; a missing value field or an extra key still
    # fails closed.
    parsed_arguments = dict(parsed_arguments)
    for optional_list in ("note_sources", "uncertainties"):
        parsed_arguments.setdefault(optional_list, [])
    if isinstance(parsed_arguments.get("evidence_sources"), dict):
        for field_name in EVIDENCE_FIELDS:
            parsed_arguments["evidence_sources"].setdefault(field_name, [])
    actual_fields = set(parsed_arguments)
    if actual_fields != expected_fields:
        raise ContractViolation(
            "tool arguments do not match the closed observation schema"
        )
    evidence_sources = parsed_arguments.get("evidence_sources")
    if not isinstance(evidence_sources, dict) or set(evidence_sources) != set(EVIDENCE_FIELDS):
        raise ContractViolation(
            "evidence_sources does not match the closed evidence schema"
        )
    resolved = {
        key: value for key, value in parsed_arguments.items()
        if key not in {"evidence_sources", "note_sources"}
    }
    quotes: dict[str, str] = {}
    for field_name in EVIDENCE_FIELDS:
        try:
            quotes[field_name] = resolve_sources(evidence_sources[field_name], raw_text)
        except ValueError as exc:
            raise ContractViolation(
                f"invalid evidence source for: {field_name}", code="invalid_evidence_source"
            ) from exc
    try:
        note_sources = parsed_arguments["note_sources"]
        resolve_sources(note_sources, raw_text)
        resolved["notes"] = [resolve_sources([source_id], raw_text) for source_id in note_sources]
    except ValueError as exc:
        raise ContractViolation("invalid note source", code="invalid_note_source") from exc
    # v3: a source attached to a field the model left null/unknown is kept as
    # a literal note instead of rejecting the whole response. The field stays
    # absent, so nothing is asserted that the model did not assert.
    for field_name in EVIDENCE_FIELDS:
        value = resolved.get(field_name)
        if quotes[field_name] and (value is None or value == "unknown"):
            if quotes[field_name] not in resolved["notes"]:
                resolved["notes"].append(quotes[field_name])
            quotes[field_name] = ""
    # v3: repeated uncertainty entries collapse instead of failing.
    seen: list[str] = []
    for item in resolved.get("uncertainties", []) or []:
        if item not in seen:
            seen.append(item)
    resolved["uncertainties"] = seen
    resolved["evidence_quotes"] = quotes
    return resolved


def _usage_int(usage: dict[str, Any], key: str) -> int | None:
    value = usage.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContractViolation(f"usage.{key} must be a non-negative integer")
    return value


def _diagnostic_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _text_length(value: Any) -> int:
    return len(value) if isinstance(value, str) else 0


def _response_diagnostics(
    body: dict[str, Any],
    plan: SmokePlan,
    response: httpx.Response,
    latency_ms: float,
) -> dict[str, Any]:
    """Summarize response shape without retaining generated text or field-note data."""

    choices = body.get("choices")
    choice = choices[0] if isinstance(choices, list) and len(choices) == 1 else {}
    choice = choice if isinstance(choice, dict) else {}
    message = choice.get("message")
    message = message if isinstance(message, dict) else {}
    tool_calls = message.get("tool_calls")
    tool_call_count = len(tool_calls) if isinstance(tool_calls, list) else None
    content_chars = _text_length(message.get("content"))
    reasoning_chars = max(
        _text_length(message.get("reasoning_content")),
        _text_length(message.get("reasoning")),
    )
    finish_reason_value = choice.get("finish_reason")
    known_finish_reasons = {"stop", "length", "tool_calls", "content_filter"}
    finish_reason = (
        finish_reason_value
        if isinstance(finish_reason_value, str) and finish_reason_value in known_finish_reasons
        else "other" if isinstance(finish_reason_value, str) else None
    )
    usage = body.get("usage")
    usage = usage if isinstance(usage, dict) else {}
    prompt_tokens = _diagnostic_int(usage.get("prompt_tokens"))
    completion_tokens = _diagnostic_int(usage.get("completion_tokens"))
    if tool_call_count == 0 and finish_reason == "length" and reasoning_chars > 0:
        response_shape = "reasoning_budget_exhausted_before_tool_call"
    elif tool_call_count == 0 and finish_reason == "length":
        response_shape = "output_budget_exhausted_before_tool_call"
    elif content_chars > 0:
        response_shape = "assistant_free_text_present"
    elif tool_call_count == 0:
        response_shape = "missing_tool_call"
    elif tool_call_count == 1:
        response_shape = "single_tool_call_present"
    elif tool_call_count is None:
        response_shape = "tool_calls_field_missing_or_invalid"
    else:
        response_shape = "multiple_tool_calls_present"
    request_id = _upstream_request_id(response) or _safe_request_id(body.get("id"))
    return {
        "response_shape": response_shape,
        "finish_reason": finish_reason,
        "tool_call_count": tool_call_count,
        "assistant_content_present": content_chars > 0,
        "assistant_content_chars": content_chars,
        "reasoning_content_present": reasoning_chars > 0,
        "reasoning_content_chars": reasoning_chars,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "completion_tokens_at_limit": (
            completion_tokens is not None
            and completion_tokens >= plan.max_completion_tokens
        ),
        "request_id": request_id,
        "http_status": response.status_code,
        "latency_ms": round(latency_ms, 1),
    }


def _safe_request_id(value: Any) -> str | None:
    if isinstance(value, str) and value and value.isascii() and all(
        character.isalnum() or character in "-_.:" for character in value
    ):
        return value[:128]
    return None


def _upstream_request_id(response: httpx.Response) -> str | None:
    for header in ("x-request-id", "x-nebius-request-id", "request-id"):
        value = _safe_request_id(response.headers.get(header))
        if value:
            return value
    return None


def parse_response(
    body: dict[str, Any], raw_text: str, plan: SmokePlan, response: httpx.Response, latency_ms: float
) -> dict[str, Any]:
    diagnostics = _response_diagnostics(body, plan, response, latency_ms)
    try:
        choices = body["choices"]
        if not isinstance(choices, list) or len(choices) != 1:
            raise ContractViolation("response must contain exactly one choice")
        choice = choices[0]
        message = choice["message"]
        if message.get("content") not in (None, ""):
            raise ContractViolation(
                "assistant emitted free text alongside the tool call",
                code="assistant_free_text",
            )
        tool_calls = message.get("tool_calls")
        if not isinstance(tool_calls, list) or len(tool_calls) != 1:
            raise ContractViolation(
                "empty or invalid assistant message: exactly one tool call is required",
                code=str(diagnostics["response_shape"]),
            )
        tool_call = tool_calls[0]
        if tool_call.get("type") != "function":
            raise ContractViolation("assistant returned a non-function tool call")
        function = tool_call["function"]
        if function.get("name") != TOOL_NAME:
            raise ContractViolation("assistant called an unexpected tool")
        arguments = function.get("arguments")
        if not isinstance(arguments, str) or not arguments.strip():
            raise ContractViolation("tool arguments must be a non-empty JSON string")
        parsed_arguments = json.loads(arguments)
        if not isinstance(parsed_arguments, dict):
            raise ContractViolation("tool arguments must decode to a JSON object")
        resolved_arguments = _resolve_arguments(parsed_arguments, raw_text)
        draft = ObservationDraft.model_validate(resolved_arguments, strict=True)
        _validate_quantities(draft)
    except ContractViolation as exc:
        if not exc.diagnostics:
            exc.diagnostics = diagnostics
        raise
    except (KeyError, IndexError, TypeError, AttributeError, json.JSONDecodeError, ValidationError) as exc:
        raise ContractViolation(
            "invalid structured observation response", diagnostics=diagnostics
        ) from exc

    try:
        _validate_evidence(draft, raw_text)
        usage = body.get("usage") or {}
        if not isinstance(usage, dict):
            raise ContractViolation("usage must be an object when present")
        input_tokens = _usage_int(usage, "prompt_tokens")
        output_tokens = _usage_int(usage, "completion_tokens")
        if input_tokens is None or output_tokens is None:
            raise ContractViolation("usage must include prompt_tokens and completion_tokens")
        if input_tokens > plan.prompt_token_budget:
            raise ContractViolation("reported prompt tokens exceed the preflight token budget")
        if output_tokens > plan.max_completion_tokens:
            raise ContractViolation("reported completion tokens exceed max_completion_tokens")
        actual_estimated_cost = (
            Decimal(input_tokens) * plan.input_price_per_million
            + Decimal(output_tokens) * plan.output_price_per_million
        ) / Decimal(1_000_000)
        if actual_estimated_cost > plan.max_cost_usd:
            raise ContractViolation("reported token usage exceeds the authorized cost cap")

        request_id = diagnostics["request_id"]
        if request_id is None:
            raise ContractViolation("response must include a request identifier")
    except ContractViolation as exc:
        if not exc.diagnostics:
            exc.diagnostics = diagnostics
        raise

    telemetry = ProviderTelemetry(
        provider="nebius",
        model=plan.model,
        latency_ms=latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        request_id=request_id,
    )
    return {
        "status": "contract_pass",
        "extraction_profile": PROFILE_ID,
        "provider": "nebius",
        "model": plan.model,
        "finish_reason": choice.get("finish_reason"),
        "observation": draft.model_dump(mode="json"),
        "telemetry": telemetry.model_dump(mode="json"),
        "estimated_usage_cost_usd": _money(actual_estimated_cost),
    }


async def execute_one_request(
    raw_text: str,
    plan: SmokePlan,
    api_key: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    payload, estimate = preflight(raw_text, plan)
    if not api_key.strip():
        raise PreflightBlocked("NEBIUS_API_KEY is required for a live request")
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=plan.timeout_seconds, transport=transport) as client:
            response = await client.post(
                f"{plan.base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.RequestError as exc:
        latency_ms = (time.perf_counter() - started) * 1000
        raise UpstreamRequestFailure(
            "Nebius transport failed; no automatic retry was attempted",
            code="upstream_transport_error",
            diagnostics={
                "http_status": None,
                "request_id": None,
                "latency_ms": round(latency_ms, 1),
            },
        ) from exc
    latency_ms = (time.perf_counter() - started) * 1000
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise UpstreamRequestFailure(
            f"Nebius returned HTTP {response.status_code}; no automatic retry was attempted",
            code="upstream_http_error",
            diagnostics={
                "http_status": response.status_code,
                "request_id": _upstream_request_id(response),
                "latency_ms": round(latency_ms, 1),
            },
        ) from exc
    try:
        body = response.json()
    except ValueError as exc:
        raise ContractViolation("Nebius returned a non-JSON response") from exc
    if not isinstance(body, dict):
        raise ContractViolation("Nebius response must be a JSON object")
    result = parse_response(body, raw_text, plan, response, latency_ms)
    result["cost_preflight"] = estimate.public_dict()
    return result


@dataclass
class GuardedNebiusExtractionProvider:
    """Application provider that can claim at most one live request per process."""

    plan: SmokePlan
    api_key: str
    transport: httpx.AsyncBaseTransport | None = None
    _request_claimed: bool = field(default=False, init=False, repr=False)
    _claim_lock: asyncio.Lock = field(
        default_factory=asyncio.Lock, init=False, repr=False
    )

    async def extract(self, raw_text: str) -> tuple[ObservationDraft, ProviderTelemetry]:
        async with self._claim_lock:
            if self._request_claimed:
                raise RuntimeError(
                    "Guarded Nebius mode permits one request per process; restart only with "
                    "fresh human authorization"
                )
            self._request_claimed = True
        try:
            result = await execute_one_request(
                raw_text,
                self.plan,
                self.api_key,
                transport=self.transport,
            )
        except httpx.HTTPError as exc:
            raise RuntimeError(
                "Nebius request failed; no automatic retry was attempted"
            ) from exc
        return (
            ObservationDraft.model_validate(result["observation"]),
            ProviderTelemetry.model_validate(result["telemetry"]),
        )


def _required_decimal_env(name: str) -> Decimal:
    raw_value = os.getenv(name, "")
    try:
        value = Decimal(raw_value)
    except InvalidOperation as exc:
        raise PreflightBlocked(f"{name} must be a positive decimal") from exc
    if not value.is_finite() or value <= 0:
        raise PreflightBlocked(f"{name} must be a positive decimal")
    return value


def _bounded_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise PreflightBlocked(f"{name} must be an integer") from exc


def provider_for_application(
    settings: Settings,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> "ExtractionProvider":
    """Select the local provider or require every live guard for Nebius."""

    from agrofield_agent.services.extraction import provider_from_settings

    if settings.provider != "nebius":
        return provider_from_settings(settings)

    require_live_confirmation(os.getenv("AGROFIELD_NEBIUS_LIVE_CONFIRMATION"))
    if not settings.nebius_api_key:
        raise PreflightBlocked("NEBIUS_API_KEY is required for guarded Nebius mode")
    reasoning_effort = os.getenv("NEBIUS_REASONING_EFFORT", "none").lower()
    allowed_reasoning_efforts = {"none", "minimal", "low", "medium", "high", "xhigh"}
    if reasoning_effort not in allowed_reasoning_efforts:
        raise PreflightBlocked(
            "NEBIUS_REASONING_EFFORT must be none, minimal, low, medium, high, or xhigh"
        )
    plan = SmokePlan(
        model=settings.nebius_model,
        base_url=settings.nebius_base_url,
        max_completion_tokens=_bounded_int_env("NEBIUS_MAX_COMPLETION_TOKENS", 1024),
        prompt_token_budget=_bounded_int_env("NEBIUS_PROMPT_TOKEN_BUDGET", 16384),
        input_price_per_million=_required_decimal_env("NEBIUS_INPUT_PRICE_PER_MILLION"),
        output_price_per_million=_required_decimal_env("NEBIUS_OUTPUT_PRICE_PER_MILLION"),
        max_cost_usd=_required_decimal_env("NEBIUS_MAX_COST_USD"),
        reasoning_effort=reasoning_effort,
    )
    _validate_plan(plan)
    return GuardedNebiusExtractionProvider(
        plan=plan,
        api_key=settings.nebius_api_key,
        transport=transport,
    )


def _decimal_argument(value: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("must be a decimal number") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive finite decimal")
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preflight and run at most one explicit Nebius compatibility request"
    )
    parser.add_argument("--note-file", type=Path, required=True)
    parser.add_argument("--model", default=os.getenv("NEBIUS_MODEL", DEFAULT_MODEL))
    parser.add_argument(
        "--base-url", default=os.getenv("NEBIUS_BASE_URL", DEFAULT_NEBIUS_BASE_URL)
    )
    parser.add_argument("--max-completion-tokens", type=int, default=1024)
    parser.add_argument("--prompt-token-budget", type=int, default=16384)
    parser.add_argument(
        "--reasoning-effort",
        choices=("none", "minimal", "low", "medium", "high", "xhigh"),
        default="none",
    )
    parser.add_argument("--input-price-per-million", type=_decimal_argument, required=True)
    parser.add_argument("--output-price-per-million", type=_decimal_argument, required=True)
    parser.add_argument("--max-cost-usd", type=_decimal_argument, required=True)
    parser.add_argument(
        "--confirm-live",
        help=f"exactly {CONFIRMATION_PHRASE}; omit for a network-free preflight",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        note = args.note_file.read_text(encoding="utf-8")
        plan = SmokePlan(
            model=args.model,
            base_url=args.base_url,
            max_completion_tokens=args.max_completion_tokens,
            prompt_token_budget=args.prompt_token_budget,
            input_price_per_million=args.input_price_per_million,
            output_price_per_million=args.output_price_per_million,
            max_cost_usd=args.max_cost_usd,
            reasoning_effort=args.reasoning_effort,
        )
        _, estimate = preflight(note, plan)
        print(
            json.dumps(
                {
                    "status": "preflight_pass",
                    "extraction_profile": PROFILE_ID,
                    "network_request_sent": False,
                    "model": plan.model,
                    "base_url": plan.base_url,
                    "cost_preflight": estimate.public_dict(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        require_live_confirmation(args.confirm_live)
        api_key = os.getenv("NEBIUS_API_KEY", "")
        result = asyncio.run(execute_one_request(note, plan, api_key))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except PreflightBlocked as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False))
        return 2
    except (ContractViolation, UpstreamRequestFailure, httpx.HTTPError) as exc:
        failure: dict[str, Any] = {
            "status": "request_or_contract_failed",
            "automatic_retry": False,
            "error": str(exc),
        }
        if isinstance(exc, (ContractViolation, UpstreamRequestFailure)):
            failure["failure_code"] = exc.code
            failure["safe_diagnostics"] = exc.diagnostics
        print(
            json.dumps(failure, ensure_ascii=False)
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
