import json
import queue
import threading
from decimal import Decimal
from http.client import HTTPConnection
from pathlib import Path
from urllib.parse import urlparse

import httpx
import pytest

from agrofield_agent import handoff_runner
from agrofield_agent.app import PROJECT_ROOT
from agrofield_agent.config import DEFAULT_NEBIUS_BASE_URL
from agrofield_agent.handoff_runner import FICTITIOUS_KEY, FORM_FIELD, HandoffRejected
from agrofield_agent.nebius_smoke import CONFIRMATION_PHRASE, DEFAULT_MODEL, SmokePlan


FORM = "application/x-www-form-urlencoded"


def make_config(**changes):
    values = {
        "mode": "mock",
        "plan": SmokePlan(
            model=DEFAULT_MODEL, base_url=DEFAULT_NEBIUS_BASE_URL,
            max_completion_tokens=1024, prompt_token_budget=16384,
            input_price_per_million=Decimal("0.06"),
            output_price_per_million=Decimal("0.24"), max_cost_usd=Decimal("0.01"),
        ),
        "note": (PROJECT_ROOT / "fixtures" / "nebius_smoke_note.txt")
        .read_text(encoding="utf-8").strip(),
        "reference": json.loads(
            (PROJECT_ROOT / "fixtures" / "nebius_smoke_reference.json")
            .read_text(encoding="utf-8")
        ),
        "port": 0,
        "idle_seconds": 10.0,
    }
    values.update(changes)
    return handoff_runner.RunnerConfig(**values)


def send(url, method="POST", *, value=FICTITIOUS_KEY, path=None, **header_changes):
    parsed = urlparse(url)
    headers = {"Origin": f"http://{parsed.netloc}", "Content-Type": FORM}
    headers.update(header_changes)
    headers = {name: item for name, item in headers.items() if item is not None}
    connection = HTTPConnection(parsed.hostname, parsed.port, timeout=10)
    connection.request(
        method, path or parsed.path,
        body=f"{FORM_FIELD}={value}" if method == "POST" else None, headers=headers,
    )
    response = connection.getresponse()
    result = response.status, response.read().decode("utf-8"), dict(response.getheaders())
    connection.close()
    return result


@pytest.fixture
def drive(monkeypatch):
    """Run the single-use server in a thread and record its temporary directory."""
    directories = []
    original = handoff_runner.tempfile.mkdtemp

    def recording_mkdtemp(*args, **kwargs):
        directories.append(Path(original(*args, **kwargs)))
        return str(directories[-1])

    monkeypatch.setattr(handoff_runner.tempfile, "mkdtemp", recording_mkdtemp)

    def start(action, **changes):
        ready, outcome = queue.Queue(), {}
        thread = threading.Thread(
            target=lambda: outcome.update(
                report=handoff_runner.run(make_config(**changes), ready.put)
            )
        )
        thread.start()
        outcome["action"] = action(ready.get(timeout=10)["url"])
        thread.join(timeout=30)
        assert not thread.is_alive()
        assert directories and not any(item.exists() for item in directories)
        return outcome["report"], outcome["action"]

    return start


def test_full_rehearsal_hands_fictitious_value_to_one_simulated_request(drive, capfd):
    def action(url):
        form = send(url, "GET")
        return form, send(url)

    report, (form, post) = drive(action)

    assert form[0] == 200 and "ENSAYO" in form[1]
    assert form[2]["Referrer-Policy"] == "same-origin"
    assert post[0] == 200 and FICTITIOUS_KEY not in post[1]
    assert report["rehearsal_checks"] == {
        name: True for name in report["rehearsal_checks"]
    }
    assert report["rehearsal_passed"] is True
    assert report["handoff"]["posts_accepted"] == report["handoff"]["body_reads"] == 1
    assert report["transport"] == {
        "simulated": True, "requests_received": 1,
        "url_model_and_bearer_matched_submission": True,
    }
    assert report["second_analysis_attempt"]["http_status"] == 503
    assert report["replay_after_single_use"] == {"http_status": 409, "blocked": True}
    assert report["analysis"]["reference_comparison"]["correct_observed"] == 8
    assert report["analysis"]["tasks_not_pending"] == 0
    assert report["nemotron_quality"] is None
    assert "not_model_evidence" in report["scope"]
    captured = capfd.readouterr()
    assert FICTITIOUS_KEY not in json.dumps(report) + captured.out + captured.err


@pytest.mark.parametrize("headers", [
    {"Origin": "null"}, {"Origin": None}, {"Origin": "https://example.invalid"},
    {"Origin": "http://127.0.0.1:1"}, {"Content-Type": "text/plain"},
    {"Host": "example.invalid"}, {"path": "/other"},
])
def test_header_guard_rejects_without_reading_body_and_consumes_the_single_use(
    drive, headers
):
    report, (status, _, _) = drive(lambda url: send(url, **headers))

    assert status == 403
    assert report["outcome"] == "handoff_rejected_by_header_guard"
    assert report["handoff"]["guard_accepted"] is False
    assert report["handoff"]["body_reads"] == report["handoff"]["posts_accepted"] == 0
    assert report["replay_after_single_use"]["blocked"] is True
    assert "transport" not in report and "analysis" not in report
    assert report["rehearsal_passed"] is False


def test_rehearsal_refuses_any_value_other_than_the_fictitious_one(drive):
    other = "looks-like-a-real-credential-0123456789"
    report, (status, body, _) = drive(lambda url: send(url, value=other))

    assert status == 400
    assert report["outcome"] == "handoff_rejected_invalid_form"
    assert "transport" not in report and report["rehearsal_passed"] is False
    assert other not in json.dumps(report) + body


@pytest.mark.parametrize("body,mode", [
    (f"{FORM_FIELD}={FICTITIOUS_KEY}".encode(), "live"),
    (f"{FORM_FIELD}={FICTITIOUS_KEY}&extra=1".encode(), "mock"),
    (f"{FORM_FIELD}={FICTITIOUS_KEY}&{FORM_FIELD}={FICTITIOUS_KEY}".encode(), "mock"),
    (f"{FORM_FIELD}=short".encode(), "live"),
    (f"{FORM_FIELD}=with+space+inside+value".encode(), "live"),
    ("api_key=ñandú-no-ascii".encode("utf-8"), "live"),
    (b"", "mock"),
])
def test_form_parser_fails_closed(body, mode):
    with pytest.raises(HandoffRejected) as error:
        handoff_runner.extract_submitted_value(body, mode)
    assert FICTITIOUS_KEY not in str(error.value)


def test_execution_error_reports_only_its_class_and_still_cleans_up(drive, monkeypatch):
    def explode(value, config, directory):
        (directory / "left-behind.sqlite3").write_bytes(b"synthetic")
        raise RuntimeError(f"must not be echoed {value}")

    monkeypatch.setattr(handoff_runner, "execute_handoff", explode)
    report, (status, body, _) = drive(lambda url: send(url))

    assert status == 502
    assert report["outcome"] == "execution_error"
    assert report["error_class"] == "RuntimeError"
    assert report["cleanup"]["temporary_directory_removed"] is True
    assert report["rehearsal_passed"] is False
    assert "must not be echoed" not in json.dumps(report) + body


def test_upstream_failure_is_not_retried_and_fails_the_rehearsal(drive, monkeypatch):
    def failing(self, request):
        self.requests += 1
        return httpx.Response(500, json={"error": "synthetic"})

    monkeypatch.setattr(handoff_runner.SimulatedNebius, "handler", failing)
    report, _ = drive(lambda url: send(url))

    assert report["analysis"]["http_status"] == 503
    assert report["analysis"]["automatic_retry"] is False
    assert report["transport"]["requests_received"] == 1
    assert report["second_analysis_attempt"]["blocked_by_one_request_guard"] is True
    assert report["cleanup"]["temporary_directory_removed"] is True
    assert report["rehearsal_passed"] is False


def test_idle_server_closes_without_executing_anything(drive):
    report, _ = drive(lambda url: None, idle_seconds=0.6)

    assert report["outcome"] == "no_post_received"
    assert report["handoff"]["posts_received"] == 0
    assert "transport" not in report and report["rehearsal_passed"] is False


@pytest.mark.parametrize("argv", [
    ["--mode", "live"],
    ["--mode", "live", "--confirm-live", "yes"],
    ["--mode", "live", "--confirm-live", CONFIRMATION_PHRASE],
    ["--mode", "mock", "--confirm-live", CONFIRMATION_PHRASE],
    ["--mode", "mock", "--max-cost-usd", "0.001"],
])
def test_cli_blocks_before_opening_a_server(argv, monkeypatch, capsys):
    monkeypatch.chdir(PROJECT_ROOT)
    monkeypatch.setattr(
        handoff_runner, "HTTPServer",
        lambda *args, **kwargs: pytest.fail("server must not start"),
    )
    assert handoff_runner.main(argv) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "blocked"


# --- batch mode -------------------------------------------------------------

def test_batch_form_runs_every_case_with_the_pasted_value_once(drive, monkeypatch):
    from agrofield_agent.nebius_eval import load_cases

    seen = {}

    async def fake_run_batch(cases, plan, api_key, max_total, *, transport=None):
        seen.update(cases=len(cases), key=api_key, cap=max_total, model=plan.model,
                    transport=transport is not None)
        return {"stop_reason": "completed", "requests_sent": len(cases),
                "accepted": len(cases), "estimated_total_cost_usd": "0.00100000"}

    monkeypatch.setattr(handoff_runner, "run_batch", fake_run_batch)
    cases = load_cases(PROJECT_ROOT / "fixtures" / "development" / "semantic_v2" / "cases.jsonl")[:3]

    def action(url):
        return send(url, "GET"), send(url)

    report, (form, post) = drive(
        action, batch_cases=cases, batch_max_total_cost_usd=Decimal("0.05")
    )

    assert "LOTE: 3 notas" in form[1] and "0.05000000" in form[1]
    assert post[0] == 200 and "stop_reason" in post[1] and "completed" in post[1]
    assert seen == {"cases": 3, "key": FICTITIOUS_KEY, "cap": Decimal("0.05"),
                    "model": DEFAULT_MODEL, "transport": True}
    assert report["scope"] == "batch_rehearsal_simulated_transport_not_model_evidence"
    assert report["batch"]["accepted"] == 3
    assert report["handoff"]["posts_accepted"] == 1
    assert "rehearsal_checks" not in report
    assert report["submitted_value"]["found_in_report"] is False
    assert report["cleanup"]["temporary_directory_removed"] is True


def test_batch_rehearsal_with_simulated_transport_sends_one_request_per_note(drive):
    from agrofield_agent.nebius_eval import load_cases

    cases = load_cases(PROJECT_ROOT / "fixtures" / "development" / "semantic_v2" / "cases.jsonl")[:2]
    report, _ = drive(lambda url: send(url), batch_cases=cases,
                      batch_max_total_cost_usd=Decimal("0.05"))

    batch = report["batch"]
    assert batch["requests_sent"] == 2 and batch["automatic_retries"] == 0
    assert report["transport"]["requests_received"] == 2
    assert batch["benchmark_validated"] is False
    assert FICTITIOUS_KEY not in json.dumps(report)


def test_batch_form_runs_extra_models_under_one_shared_cap(drive, monkeypatch):
    from agrofield_agent.nebius_eval import load_cases

    calls = []

    async def fake_run_batch(cases, plan, api_key, max_total, *, transport=None):
        calls.append((plan.model, max_total))
        return {"model": plan.model, "stop_reason": "completed", "requests_sent": len(cases),
                "accepted": len(cases), "estimated_total_cost_usd": "0.01000000",
                "records": [{"case_id": "x"}]}

    monkeypatch.setattr(handoff_runner, "run_batch", fake_run_batch)
    cases = load_cases(PROJECT_ROOT / "fixtures" / "development" / "semantic_v3" / "cases.jsonl")[:2]
    super_plan = SmokePlan(
        model="nvidia/nemotron-3-super-120b-a12b", base_url=DEFAULT_NEBIUS_BASE_URL,
        max_completion_tokens=1024, prompt_token_budget=16384,
        input_price_per_million=Decimal("0.3"), output_price_per_million=Decimal("0.9"),
        max_cost_usd=Decimal("0.01"),
    )
    report, _ = drive(lambda url: send(url), batch_cases=cases,
                      batch_max_total_cost_usd=Decimal("0.05"),
                      batch_extra_plans=(super_plan,))

    assert calls == [(DEFAULT_MODEL, Decimal("0.05")),
                     ("nvidia/nemotron-3-super-120b-a12b", Decimal("0.04"))]
    assert report["batch"]["models"] == [DEFAULT_MODEL, "nvidia/nemotron-3-super-120b-a12b"]
    assert report["batch"]["estimated_total_cost_usd"] == "0.02000000"
    assert report["batch"]["requests_sent"] == 4 and report["batch"]["records"] == []
    assert [item["model"] for item in report["batches"]] == report["batch"]["models"]


@pytest.mark.parametrize("argv", [
    ["--mode", "mock", "--extra-model", "nvidia/x,0.3,0.9"],
    ["--mode", "mock", "--batch", "--extra-model", "nvidia/x,0.3"],
    ["--mode", "live", "--batch", "--input-price-per-million", "0.06",
     "--output-price-per-million", "0.24"],
    ["--mode", "live", "--batch", "--input-price-per-million", "0.06",
     "--output-price-per-million", "0.24", "--confirm-live", CONFIRMATION_PHRASE],
    ["--mode", "live", "--batch", "--confirm-live", "RUN_NEBIUS_EVAL_BATCH"],
    ["--mode", "mock", "--batch", "--confirm-live", "RUN_NEBIUS_EVAL_BATCH"],
    ["--mode", "mock", "--batch", "--max-requests", "0"],
])
def test_batch_cli_blocks_without_its_own_confirmation_and_prices(argv, monkeypatch, capsys):
    monkeypatch.chdir(PROJECT_ROOT)
    monkeypatch.setattr(
        handoff_runner, "HTTPServer",
        lambda *args, **kwargs: pytest.fail("server must not start"),
    )
    assert handoff_runner.main(argv) == 2
    assert json.loads(capsys.readouterr().out.splitlines()[-1])["status"] == "blocked"
