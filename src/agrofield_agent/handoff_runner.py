"""Single-use browser -> loopback -> /api/analyze runner for one guarded request.

Default mode is a rehearsal: the Nebius transport is simulated in process, only a
fixed fictitious value is accepted from the form and nothing leaves the machine.
Live mode shares every step except the transport and requires the exact one-use
confirmation, current prices and a cap. The submitted value is never written to
the environment, a file, a log or the report.
"""
from __future__ import annotations

import argparse
import asyncio
import gc
import hashlib
import hmac
import html
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Literal, Mapping
from urllib.parse import parse_qs

import httpx

from agrofield_agent.config import DEFAULT_NEBIUS_BASE_URL, Settings
from agrofield_agent.nebius_smoke import (
    CONFIRMATION_PHRASE,
    DEFAULT_MODEL,
    GuardedNebiusExtractionProvider,
    PreflightBlocked,
    SmokePlan,
    _decimal_argument,
    _money,
    preflight,
    require_live_confirmation,
)
from agrofield_agent.nebius_eval import (
    BATCH_CONFIRMATION_PHRASE,
    load_cases,
    plan_batch,
    run_batch,
)
from agrofield_agent.smoke_audit import compare_fields

FICTITIOUS_KEY = "agrofield-rehearsal-value-not-a-credential"
DEFAULT_PORT = 18093
FIELD_ID = "lote-bajo"
FORM_FIELD = "api_key"
MAX_BODY_BYTES = 2048
REFERRER_POLICY = "same-origin"
_ISOLATED_ENV = {
    "AGROFIELD_PROVIDER": "local",
    "AGROFIELD_RECORDING_MODE": "",
    "NEBIUS_API_KEY": "",
    "TAVILY_API_KEY": "",
}


class HandoffRejected(Exception):
    """The submitted form was refused; the message never contains its content."""


@dataclass(frozen=True)
class RunnerConfig:
    mode: Literal["mock", "live"]
    plan: SmokePlan
    note: str
    reference: dict[str, Any]
    port: int = DEFAULT_PORT
    idle_seconds: float = 180.0
    linger_seconds: float = 5.0
    pricing_basis: str = "historical_2026-09-15_not_current"
    # Batch mode: the pasted value runs every case through nebius_eval instead
    # of one /api/analyze request. Same single-use form, same cleanup.
    batch_cases: list[dict[str, Any]] | None = None
    batch_max_total_cost_usd: Decimal | None = None
    # Further plans (other models, their own prices) run after `plan` with
    # the remaining shared cap, each one its own capped batch.
    batch_extra_plans: tuple[SmokePlan, ...] = ()


@dataclass
class _State:
    claimed: bool = False
    posts_received: int = 0
    posts_accepted: int = 0
    posts_blocked_after_first: int = 0
    body_reads: int = 0
    header_checks: dict[str, bool] = field(default_factory=dict)
    outcome: str = "no_post_received"
    execution: dict[str, Any] = field(default_factory=dict)


def check_headers(
    path: str, headers: Mapping[str, str], route: str, origin: str
) -> dict[str, bool]:
    checks = {
        "path_matches": path == route,
        "host_matches": headers.get("Host") == origin.removeprefix("http://"),
        "origin_matches": headers.get("Origin") == origin,
        "content_type_matches": headers.get("Content-Type", "").split(";")[0].strip()
        == "application/x-www-form-urlencoded",
    }
    return {**checks, "guard_accepted": all(checks.values())}


def extract_submitted_value(body: bytes, mode: str) -> str:
    try:
        fields = parse_qs(
            body.decode("ascii"), keep_blank_values=True, strict_parsing=True
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise HandoffRejected("malformed form body") from exc
    if set(fields) != {FORM_FIELD} or len(fields[FORM_FIELD]) != 1:
        raise HandoffRejected("form must contain exactly one expected field")
    value = fields[FORM_FIELD][0]
    if not 8 <= len(value) <= 512 or any(not 33 <= ord(char) <= 126 for char in value):
        raise HandoffRejected("submitted value has an invalid shape")
    is_fictitious = hmac.compare_digest(value, FICTITIOUS_KEY)
    if mode == "mock" and not is_fictitious:
        raise HandoffRejected("the rehearsal accepts only its fixed fictitious value")
    if mode == "live" and is_fictitious:
        raise HandoffRejected("the fictitious rehearsal value cannot be used live")
    return value


def simulated_arguments() -> dict[str, Any]:
    """Tool arguments for the fixed synthetic note; test data, not model output."""
    return {
        "crop_stage": "V3", "event_type": "flooding", "event_hours_ago": 18,
        "access_safe": True, "sample_points": 6, "affected_area_pct": 35,
        "standing_water_pct": 35, "water_duration_hours": 14, "lodging_pct": None,
        "stem_damage_pct": None, "stand_count_per_m": None,
        "general_condition": "unknown", "note_sources": [],
        "evidence_sources": {
            "crop_stage": ["S01"], "event_type": ["S04"], "event_hours_ago": ["S02"],
            "access_safe": ["S02"], "sample_points": ["S03"],
            "affected_area_pct": ["S04"], "standing_water_pct": ["S04"],
            "water_duration_hours": ["S04"], "lodging_pct": [], "stem_damage_pct": [],
            "stand_count_per_m": [], "general_condition": [],
        },
        "uncertainties": [],
    }


class SimulatedNebius:
    """In-process stand-in for the endpoint; counts and checks what it receives."""

    def __init__(self, plan: SmokePlan, expected_value_sha256: str) -> None:
        self._expected_url = f"{plan.base_url.rstrip('/')}/chat/completions"
        self._expected_model = plan.model
        self._expected_value_sha256 = expected_value_sha256
        self.requests = 0
        self.all_requests_well_formed = True

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests += 1
        bearer = request.headers.get("Authorization", "").removeprefix("Bearer ")
        try:
            model = json.loads(request.content).get("model")
        except ValueError:
            model = None
        self.all_requests_well_formed &= (
            request.method == "POST"
            and str(request.url) == self._expected_url
            and model == self._expected_model
            and hashlib.sha256(bearer.encode("utf-8")).hexdigest()
            == self._expected_value_sha256
        )
        return httpx.Response(200, json={
            "id": "chatcmpl-simulated",
            "choices": [{
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant", "content": None,
                    "tool_calls": [{
                        "id": "call-simulated", "type": "function",
                        "function": {
                            "name": "record_field_observation",
                            "arguments": json.dumps(simulated_arguments()),
                        },
                    }],
                },
            }],
            "usage": {"prompt_tokens": 900, "completion_tokens": 120},
        })

    def public_dict(self) -> dict[str, Any]:
        return {
            "simulated": True,
            "requests_received": self.requests,
            "url_model_and_bearer_matched_submission": (
                self.requests > 0 and self.all_requests_well_formed
            ),
        }


def _import_app_isolated(directory: Path):
    """Import the app module without touching persistent data or credentials."""
    overrides = {**_ISOLATED_ENV, "AGROFIELD_DB_PATH": str(directory / "import.sqlite3")}
    previous = {name: os.environ.get(name) for name in overrides}
    os.environ.update(overrides)
    try:
        import agrofield_agent.app as app_module
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
    return app_module


def _summarize_analysis(response: Any, config: RunnerConfig) -> dict[str, Any]:
    summary: dict[str, Any] = {"route": "/api/analyze", "http_status": response.status_code}
    body = response.json()
    if response.status_code != 200:
        summary.update({
            name: body.get(name)
            for name in ("detail", "failure_code", "safe_diagnostics", "automatic_retry")
            if name in body
        })
        return summary
    telemetry = body["telemetry"]
    observation = {
        name: value for name, value in body["observation"].items()
        if name not in {"raw_text", "field_id"}
    }
    statuses = [task["status"] for task in body["proposed_tasks"]]
    cost = (
        Decimal(telemetry["input_tokens"]) * config.plan.input_price_per_million
        + Decimal(telemetry["output_tokens"]) * config.plan.output_price_per_million
    ) / Decimal(1_000_000)
    summary.update({
        "policy_status": body["status"],
        "missing_critical": body["missing_critical"],
        "tasks_pending": statuses.count("pending"),
        "tasks_not_pending": len(statuses) - statuses.count("pending"),
        "official_alerts": len(body["official_alerts"]),
        "telemetry": telemetry,
        "estimated_usage_cost_usd": _money(cost),
        "observation": observation,
        "observation_sha256": hashlib.sha256(
            json.dumps(observation, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "reference_comparison": {
            "reference_status": config.reference["reference_status"],
            **compare_fields(observation, config.reference["expected"]),
        },
    })
    return summary


def _value_in_files(directory: Path, value: str) -> bool:
    needle = value.encode("ascii")
    return any(
        needle in path.read_bytes() for path in directory.rglob("*") if path.is_file()
    )


def _submitted_value_checks(value: str, config: RunnerConfig, directory: Path,
                            result: dict[str, Any]) -> dict[str, Any]:
    return {
        "fictitious": config.mode == "mock",
        "found_in_environment": value in os.environ.values(),
        "found_in_temporary_files": _value_in_files(directory, value),
        "found_in_report": value in json.dumps(result, ensure_ascii=False),
    }


def _execute_batch(value: str, config: RunnerConfig, directory: Path) -> dict[str, Any]:
    """Run the capped development batch with the pasted value; one request per note."""
    simulated = None
    transport = None
    if config.mode == "mock":
        simulated = SimulatedNebius(
            config.plan, hashlib.sha256(value.encode("utf-8")).hexdigest()
        )
        transport = httpx.MockTransport(simulated.handler)
    remaining = config.batch_max_total_cost_usd
    batches: list[dict[str, Any]] = []
    for plan in (config.plan, *config.batch_extra_plans):
        if remaining <= 0:
            break
        batch = asyncio.run(run_batch(
            config.batch_cases, plan, value, remaining, transport=transport,
        ))
        remaining -= Decimal(batch["estimated_total_cost_usd"])
        batches.append(batch)
    report = batches[0]
    result: dict[str, Any] = {"tavily_enabled": False, "batch": report}
    if len(batches) > 1:
        result["batches"] = batches
        result["batch"] = {
            **report,
            "models": [item["model"] for item in batches],
            "stop_reason": "completed" if all(
                item["stop_reason"] == "completed" for item in batches
            ) else "partial",
            "requests_sent": sum(item["requests_sent"] for item in batches),
            "accepted": sum(item["accepted"] for item in batches),
            "estimated_total_cost_usd": _money(
                sum((Decimal(item["estimated_total_cost_usd"]) for item in batches),
                    Decimal(0))
            ),
            "records": [],
        }
    result["transport"] = (
        simulated.public_dict() if simulated is not None
        else {"simulated": False, "automatic_retries": 0}
    )
    result["submitted_value"] = _submitted_value_checks(value, config, directory, result)
    return result


def execute_handoff(value: str, config: RunnerConfig, directory: Path) -> dict[str, Any]:
    if config.batch_cases is not None:
        return _execute_batch(value, config, directory)
    """Run the fixed note through the real FastAPI route with one guarded provider."""
    from fastapi.testclient import TestClient

    from agrofield_agent.repository import Repository

    app_module = _import_app_isolated(directory)
    simulated = None
    transport = None
    if config.mode == "mock":
        simulated = SimulatedNebius(
            config.plan, hashlib.sha256(value.encode("utf-8")).hexdigest()
        )
        transport = httpx.MockTransport(simulated.handler)
    provider = GuardedNebiusExtractionProvider(
        plan=config.plan, api_key=value, transport=transport
    )
    settings = Settings(
        provider="nebius",
        database_path=directory / "handoff.sqlite3",
        nebius_api_key=None,
        nebius_base_url=config.plan.base_url,
        nebius_model=config.plan.model,
        tavily_api_key=None,
        tavily_include_domains=(),
    )
    repository = Repository(
        settings.database_path, app_module.PACKAGE_ROOT / "data" / "fields.json"
    )
    request = {"field_id": FIELD_ID, "raw_text": config.note, "use_tavily": False}
    result: dict[str, Any] = {"tavily_enabled": False}
    with TestClient(
        app_module.create_app(settings, repository, extraction_provider=provider)
    ) as client:
        result["analysis"] = _summarize_analysis(
            client.post("/api/analyze", json=request), config
        )
        if simulated is not None:
            # Only the rehearsal probes the lock; live mode never asks twice.
            second = client.post("/api/analyze", json=request)
            result["second_analysis_attempt"] = {
                "http_status": second.status_code,
                "blocked_by_one_request_guard": second.status_code == 503
                and "one request per process" in str(second.json().get("detail")),
            }
    del provider, repository, client
    gc.collect()
    if simulated is not None:
        result["transport"] = simulated.public_dict()
    else:
        result["transport"] = {"simulated": False, "automatic_retries": 0}
    result["submitted_value"] = _submitted_value_checks(value, config, directory, result)
    return result


def _replay_probe(port: int, route: str, origin: str, sink: dict[str, Any]) -> None:
    """Resubmit a well-formed form after the single use; it must be refused."""
    try:
        connection = HTTPConnection("127.0.0.1", port, timeout=5)
        connection.request(
            "POST", route, body=f"{FORM_FIELD}={FICTITIOUS_KEY}",
            headers={"Origin": origin,
                     "Content-Type": "application/x-www-form-urlencoded"},
        )
        sink["http_status"] = connection.getresponse().status
        connection.close()
    except OSError:
        sink["http_status"] = None


def _remove_directory(directory: Path) -> bool:
    for _ in range(20):
        gc.collect()  # Windows keeps SQLite files locked until handles are released.
        shutil.rmtree(directory, ignore_errors=True)
        if not directory.exists():
            return True
        time.sleep(0.25)
    return False


def _form_page(config: RunnerConfig) -> str:
    mode = config.mode
    scope = ""
    if config.batch_cases is not None:
        models = ", ".join(html.escape(item.model) for item in (config.plan, *config.batch_extra_plans))
        scope = (f"<p>LOTE: {len(config.batch_cases)} notas sintéticas, modelos "
                 f"{models}, tope total "
                 f"US${_money(config.batch_max_total_cost_usd)}, una solicitud por nota, "
                 "sin reintentos.</p>")
    if mode == "mock":
        notice = ("<h1>ENSAYO · transporte Nebius simulado</h1><p>Valor ficticio fijo. "
                  "<strong>No pegar claves reales.</strong></p>")
        control = (f'<input name="{FORM_FIELD}" value="{FICTITIOUS_KEY}" readonly '
                   'size="48">')
    else:
        notice = ("<h1>EJECUCIÓN REAL · una sola solicitud</h1><p>La clave temporal se "
                  "usa una vez en memoria y no se guarda.</p>")
        control = (f'<input name="{FORM_FIELD}" type="password" autocomplete="off" '
                   'required size="48">')
    return ("<title>AgroField · traspaso local de un solo uso</title>" + notice + scope
            + '<form method="post" autocomplete="off"><label>Valor '
            + control + "</label> <button>Enviar una sola vez</button></form>")


def run(config: RunnerConfig, announce=None) -> dict[str, Any]:
    """Serve one form, accept at most one POST, and always clean up."""
    _, estimate = preflight(config.note, config.plan)
    state = _State()
    replay: dict[str, Any] = {}
    directory = Path(tempfile.mkdtemp(prefix="agrofield-handoff-"))
    route = "/" + secrets.token_urlsafe(24)
    server_closed = False

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, code: int, content: str) -> None:
            body = content.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", REFERRER_POLICY)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; form-action 'self'; frame-ancestors 'none'",
            )
            self.end_headers()
            try:
                self.wfile.write(body)
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass

        def refuse(self, code: int, content: str) -> None:
            """Answer, then drop the unread form without decoding or keeping it.

            Closing a Windows socket with unread input resets the connection and
            the browser never sees the refusal, so the bytes are drained into a
            scratch buffer that is zeroed immediately.
            """
            self.reply(code, content)
            scratch = bytearray(MAX_BODY_BYTES)
            try:
                self.connection.shutdown(socket.SHUT_WR)
                self.connection.settimeout(0.5)
                for _ in range(32):
                    if not self.connection.recv_into(scratch):
                        break
            except OSError:
                pass
            finally:
                scratch[:] = bytes(len(scratch))

        def do_GET(self):
            if (state.claimed or self.path != route
                    or self.headers.get("Host") != origin.removeprefix("http://")):
                return self.reply(404, "Unavailable")
            self.reply(200, _form_page(config))

        def do_POST(self):
            state.posts_received += 1
            if state.claimed:
                state.posts_blocked_after_first += 1
                return self.refuse(409, "Blocked: this form was already used once")
            # Any first POST consumes the single use, accepted or not.
            state.claimed = True
            state.header_checks = check_headers(self.path, self.headers, route, origin)
            if not state.header_checks["guard_accepted"]:
                state.outcome = "handoff_rejected_by_header_guard"
                return self.refuse(403, "Blocked")
            try:
                length = int(self.headers.get("Content-Length", ""))
            except ValueError:
                length = -1
            if not 0 < length <= MAX_BODY_BYTES:
                state.outcome = "handoff_rejected_invalid_length"
                return self.refuse(400, "Blocked")
            body = self.rfile.read(length)
            state.body_reads += 1
            try:
                value = extract_submitted_value(body, config.mode)
            except HandoffRejected as exc:
                state.outcome = "handoff_rejected_invalid_form"
                state.execution = {"error": str(exc)}
                return self.reply(400, "Blocked")
            finally:
                del body
            state.posts_accepted += 1
            try:
                state.execution = execute_handoff(value, config, directory)
                state.outcome = "executed"
            except Exception as exc:  # report the class only; never a message or trace
                state.outcome = "execution_error"
                state.execution = {"error_class": type(exc).__name__}
            finally:
                del value
            summary: dict[str, Any] = {"mode": config.mode, "outcome": state.outcome}
            batch = state.execution.get("batch")
            if batch is not None:
                ok = batch.get("stop_reason") == "completed"
                summary.update({
                    "requests_sent": batch.get("requests_sent"),
                    "accepted": batch.get("accepted"),
                    "stop_reason": batch.get("stop_reason"),
                    "estimated_total_cost_usd": batch.get("estimated_total_cost_usd"),
                })
            else:
                status = state.execution.get("analysis", {}).get("http_status")
                ok = status == 200
                summary["analyze_http_status"] = status
            self.reply(
                200 if ok else 502,
                "<title>Traspaso terminado</title><pre>" + html.escape(json.dumps(
                    summary, indent=2)) + "</pre>"
                "<p>El detalle saneado quedó en la terminal. Ya puede cerrar esta "
                "pestaña.</p>",
            )

    class Server(HTTPServer):
        def handle_error(self, request, client_address):
            print("HANDOFF_SERVER_REQUEST_ERROR", file=sys.stderr, flush=True)

    try:
        with Server(("127.0.0.1", config.port), Handler) as server:
            server.timeout = 0.5
            port = server.server_address[1]
            origin = f"http://127.0.0.1:{port}"
            if announce:
                announce({"url": origin + route, "mode": config.mode,
                          "external_requests_possible": config.mode == "live"})
            deadline = time.monotonic() + config.idle_seconds
            while not state.claimed and time.monotonic() < deadline:
                server.handle_request()
            if state.claimed and config.mode == "mock":
                probe = threading.Thread(
                    target=_replay_probe, args=(port, route, origin, replay)
                )
                probe.start()
                linger = time.monotonic() + config.linger_seconds
                while probe.is_alive() and time.monotonic() < linger:
                    server.handle_request()
                probe.join(timeout=5)
        server_closed = True
    finally:
        temporary_directory_removed = _remove_directory(directory)

    report: dict[str, Any] = {
        "scope": _scope(config),
        "mode": config.mode,
        "model": config.plan.model,
        "outcome": state.outcome,
        "referrer_policy": REFERRER_POLICY,
        "pricing_basis": config.pricing_basis,
        "cost_preflight": estimate.public_dict(),
        "max_cost_usd": _money(config.plan.max_cost_usd),
        "note_sha256": hashlib.sha256(config.note.encode("utf-8")).hexdigest(),
        "handoff": {
            **state.header_checks,
            "posts_received": state.posts_received,
            "posts_accepted": state.posts_accepted,
            "posts_blocked_after_first": state.posts_blocked_after_first,
            "body_reads": state.body_reads,
        },
        **state.execution,
        "cleanup": {
            "server_closed": server_closed,
            "temporary_directory_removed": temporary_directory_removed,
        },
    }
    if config.mode == "mock" and config.batch_cases is None:
        report["replay_after_single_use"] = {
            "http_status": replay.get("http_status"),
            "blocked": replay.get("http_status") == 409,
        }
        report["rehearsal_checks"] = rehearsal_checks(report)
        report["rehearsal_passed"] = all(report["rehearsal_checks"].values())
        report["nemotron_quality"] = None
    return report


def _scope(config: RunnerConfig) -> str:
    if config.batch_cases is not None:
        return ("batch_rehearsal_simulated_transport_not_model_evidence"
                if config.mode == "mock"
                else "capped_live_batch_synthetic_development_not_a_validated_benchmark")
    return ("full_handoff_rehearsal_simulated_transport_not_model_evidence"
            if config.mode == "mock" else "single_authorized_live_request")


def rehearsal_checks(report: dict[str, Any]) -> dict[str, bool]:
    handoff = report["handoff"]
    analysis = report.get("analysis", {})
    transport = report.get("transport", {})
    value = report.get("submitted_value", {})
    comparison = analysis.get("reference_comparison", {})
    return {
        "host_origin_path_and_content_type_matched": handoff.get("guard_accepted") is True,
        "exactly_one_post_accepted_and_one_body_read": handoff["posts_accepted"] == 1
        and handoff["body_reads"] == 1,
        "replayed_post_blocked_without_reading_body": report["replay_after_single_use"][
            "blocked"] and handoff["posts_blocked_after_first"] >= 1,
        "analyze_route_accepted_guarded_provider_output": analysis.get("http_status") == 200
        and analysis.get("telemetry", {}).get("provider") == "nebius",
        "simulated_transport_received_exactly_one_request": transport.get(
            "requests_received") == 1
        and transport.get("url_model_and_bearer_matched_submission") is True,
        "second_analysis_blocked_by_one_request_guard": report.get(
            "second_analysis_attempt", {}).get("blocked_by_one_request_guard") is True,
        "no_task_decided_without_human_and_tavily_off": analysis.get("tasks_not_pending") == 0
        and analysis.get("official_alerts") == 0
        and report.get("tavily_enabled") is False,
        "submitted_value_not_in_environment_files_or_report": value != {}
        and not any(value[name] for name in (
            "found_in_environment", "found_in_temporary_files", "found_in_report")),
        "comparator_reads_all_twelve_fields": comparison.get("fields") == 12
        and comparison.get("errors") == [],
        "server_closed_and_temporary_sqlite_removed": all(report["cleanup"].values()),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("mock", "live"), default="mock")
    parser.add_argument("--note-file", type=Path, default=Path("fixtures/nebius_smoke_note.txt"))
    parser.add_argument(
        "--reference", type=Path, default=Path("fixtures/nebius_smoke_reference.json")
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--idle-seconds", type=float, default=180.0,
                        help="close the unused form after this many seconds (30-900)")
    parser.add_argument("--input-price-per-million", type=_decimal_argument)
    parser.add_argument("--output-price-per-million", type=_decimal_argument)
    parser.add_argument("--max-cost-usd", type=_decimal_argument, default=Decimal("0.01"))
    parser.add_argument("--confirm-live", help=f"exactly {CONFIRMATION_PHRASE}; live mode only")
    parser.add_argument("--report-file", type=Path, help="also write the sanitized report here")
    parser.add_argument("--batch", action="store_true",
                        help="run the capped development batch instead of one request")
    parser.add_argument("--dataset", type=Path,
                        default=Path("fixtures/development/semantic_v3/cases.jsonl"))
    parser.add_argument("--model", default=DEFAULT_MODEL, help="batch mode only")
    parser.add_argument("--extra-model", action="append", default=[],
                        metavar="MODEL,INPUT_PRICE,OUTPUT_PRICE",
                        help="batch mode only: another model with its own prices")
    parser.add_argument("--max-requests", type=int, default=20, help="batch mode only")
    parser.add_argument("--max-total-cost-usd", type=_decimal_argument,
                        default=Decimal("0.05"), help="batch mode only")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        prices = (args.input_price_per_million, args.output_price_per_million)
        if args.mode == "live":
            if args.batch:
                if args.confirm_live != BATCH_CONFIRMATION_PHRASE:
                    raise PreflightBlocked(
                        f"batch blocked; pass --confirm-live {BATCH_CONFIRMATION_PHRASE} "
                        "only after the owner authorizes this request count and cap"
                    )
            else:
                require_live_confirmation(args.confirm_live)
            if None in prices:
                raise PreflightBlocked("live mode requires both prices, verified today")
            basis = "operator_supplied_for_this_run"
        elif args.confirm_live is not None:
            raise PreflightBlocked("--confirm-live is not accepted in rehearsal mode")
        else:
            prices = (prices[0] or Decimal("0.06"), prices[1] or Decimal("0.24"))
            basis = "historical_2026-09-15_not_current"
        if not 30 <= args.idle_seconds <= 900:
            raise PreflightBlocked("--idle-seconds must be between 30 and 900")
        note = args.note_file.read_text(encoding="utf-8").strip()
        reference = json.loads(args.reference.read_text(encoding="utf-8"))
        if reference["normalized_note_sha256"] != hashlib.sha256(
            note.encode("utf-8")
        ).hexdigest():
            raise PreflightBlocked("reference does not belong to this note")
        batch_cases = None
        extra_plans: list[SmokePlan] = []
        if args.batch:
            if not 1 <= args.max_requests <= 200:
                raise PreflightBlocked("--max-requests must be between 1 and 200")
            batch_cases = load_cases(args.dataset)[: args.max_requests]
            for spec in args.extra_model:
                parts = spec.split(",")
                if len(parts) != 3:
                    raise PreflightBlocked("--extra-model needs MODEL,INPUT_PRICE,OUTPUT_PRICE")
                extra_plans.append(SmokePlan(
                    model=parts[0], base_url=DEFAULT_NEBIUS_BASE_URL,
                    max_completion_tokens=1024, prompt_token_budget=16384,
                    input_price_per_million=_decimal_argument(parts[1]),
                    output_price_per_million=_decimal_argument(parts[2]),
                    max_cost_usd=args.max_cost_usd,
                ))
        elif args.extra_model:
            raise PreflightBlocked("--extra-model is only valid with --batch")
        config = RunnerConfig(
            mode=args.mode,
            plan=SmokePlan(
                model=args.model if args.batch else DEFAULT_MODEL,
                base_url=DEFAULT_NEBIUS_BASE_URL,
                max_completion_tokens=1024, prompt_token_budget=16384,
                input_price_per_million=prices[0], output_price_per_million=prices[1],
                max_cost_usd=args.max_cost_usd,
            ),
            note=note, reference=reference, port=args.port, pricing_basis=basis,
            idle_seconds=args.idle_seconds,
            batch_cases=batch_cases,
            batch_max_total_cost_usd=args.max_total_cost_usd if args.batch else None,
            batch_extra_plans=tuple(extra_plans),
        )
        if batch_cases is not None:
            for item in (config.plan, *config.batch_extra_plans):
                print(json.dumps({"status": "batch_plan", "network_request_sent": False,
                                  "model": item.model,
                                  **plan_batch(batch_cases, item, args.max_total_cost_usd)},
                                 indent=2), flush=True)
        report = run(config, lambda item: print(json.dumps(item), flush=True))
    except PreflightBlocked as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False))
        return 2
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    print(serialized, flush=True)
    if args.report_file:
        args.report_file.write_text(serialized + "\n", encoding="utf-8")
    print("HANDOFF_RUNNER_CLOSED", flush=True)
    if report["outcome"] == "no_post_received":
        return 4
    if "batch" in report:
        return 0 if report["batch"].get("stop_reason") == "completed" else 3
    if args.mode == "mock":
        return 0 if report["rehearsal_passed"] else 1
    return 0 if report.get("analysis", {}).get("http_status") == 200 else 3


if __name__ == "__main__":
    raise SystemExit(main())
