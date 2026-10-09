# Full handoff rehearsal with simulated transport — 2026-10-09

## Outcome

`REHEARSAL_PASSED_NO_INFERENCE`. The complete browser → loopback server →
FastAPI `/api/analyze` → guarded provider path ran with a **simulated Nebius
transport and a fixed fictitious value**. No key was created, no request left the
machine, and the single authorized Nano inference remains **unconsumed**.
Lifetime real inference count is still four. Nothing here is model evidence:
`nemotron_quality` is null and the simulated response is test data.

## What was added

- `python -m agrofield_agent.handoff_runner` (default `--mode mock`). It serves
  one form on `127.0.0.1:18093` under a random single-use path with
  `Referrer-Policy: same-origin`, then runs the fixed note
  `fixtures/nebius_smoke_note.txt` through the real route in process.
- `create_app()` accepts an optional `extraction_provider`, so the runner injects
  the one-request guarded provider without environment variables.
- 24 tests in `tests/test_handoff_runner.py`. Suite: **157 passing**; freezes
  34/34 and 8/8 unchanged; `policy.py` hash unchanged.

## Controls verified in the real in-app browser

| Control | Result |
|---|---|
| Host, Origin, path and content type match exactly | pass |
| Exactly one POST accepted and one body read | pass |
| Replayed well-formed POST after the single use | HTTP 409, body not parsed |
| Simulated transport received exactly one request, with the expected URL, model and submitted bearer | pass |
| Second `/api/analyze` attempt | HTTP 503, one-request guard, transport still at one |
| Submitted value absent from environment, temporary files, report, stdout and stderr | pass |
| Tavily off, no task decided without a human | pass |
| Server closed and temporary SQLite directory removed on Windows | pass |

Any first POST consumes the single use, including one rejected by the header
guard (`Origin: null`, foreign origin, wrong port, Host, type or path); the tests
cover each. A refused form is drained into a zeroed scratch buffer without being
decoded, because closing a Windows socket with unread input resets the
connection before the browser can show the refusal.

Rehearsal mode refuses any value other than its fictitious constant, so a real
key pasted by mistake is dropped before execution.

## Reproduce without credentials

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts='' -q
.\.venv\Scripts\python.exe -m agrofield_agent.handoff_runner
# Open the printed loopback URL and submit the prefilled fictitious value once.
# Expect rehearsal_passed=true and exit code 0.
```

## Live mode, not run

`--mode live` uses the same path with the real transport. It refuses to start
without `--confirm-live RUN_ONE_NEBIUS_REQUEST`, both prices verified that day
and a cap; it never probes a second request. It has **not** been executed.
Before any use: recheck promotional credit, Nano prices, balance and
`Usage stops after the trial` on the day. The owner pastes the temporary key into
the local form and revokes it immediately afterwards.
