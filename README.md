# AgroField Agent

AgroField Agent is a protocol-aware field-scouting coordinator for soybean fields after heavy rain, wind, or hail. It turns a spoken or typed field note, weather context, and field history into a structured evidence packet, highlights what still needs to be checked, ranks follow-up work, and requires human approval before creating a decision.

This is deliberately not a general agronomy chatbot. The first vertical slice is **post-weather-event soybean triage**.

## Why this workflow

Field notes are easy to capture and easy to over-trust. A plausible narrative can omit the crop stage, sample size, affected area, duration of standing water, stem damage, or access safety. AgroField Agent treats those omissions as first-class output. The model may extract and summarize evidence, but deterministic safety gates decide whether a recommendation is ready for review.

## Current MVP

- Mobile-first demo with four soybean fields and traceable history.
- Text capture plus browser speech-to-text when the browser supports it.
- Structured Spanish extraction through either a local deterministic provider or NVIDIA Nemotron on Nebius Token Factory.
- Evidence-completeness gate and targeted follow-up questions.
- Explainable priority score across fields.
- Proposed tasks that remain pending until explicit human approval.
- Immutable audit events stored in SQLite.
- Optional Tavily adapter restricted to authoritative agronomy and weather domains.
- Offline evaluation harness for extraction, critical omissions, ranking, latency, and estimated inference cost.
- Blind agronomy benchmark candidate with 30 cases, physically separated Phase A/B packets, strict human-evidence gates, E1–E8 failure analysis, and reviewer-agreement metrics.

## Quick start (local, zero API cost)

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -e ".[dev]"
python -m agrofield_agent
```

Open `http://127.0.0.1:8000`.

For a repeatable screen-recording rehearsal, start the dedicated mode:

```bash
python -m agrofield_agent --recording
```

Every recording-mode start creates a fresh temporary SQLite database, forces the local deterministic provider, disables Nebius and Tavily credentials for that process, and labels the interface `ENSAYO LOCAL · SINTÉTICO`. Closing the server removes the temporary database and restores the original environment.

Run tests and the evaluation:

```bash
pytest
python -m agrofield_agent.evaluate fixtures/eval_cases.jsonl
```

Run the harder blind-benchmark candidate:

```bash
python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl
```

The 30-case set is synthetic and currently has **zero human agronomy reviews and zero completed interviews**. The user reports valid mandatory written consent and evaluator-required anonymous/aggregated evidence scopes for 5/5 interviews and the three independent roles `R01`, `R02`, and `A01`. Recruitment is therefore ready for email fieldwork, but no human evidence has yet been collected, sanitized, or ingested. Its output is labeled `provisional_candidate_reference`; it is not a Nemotron result or agronomist-validated evidence. All five P0 blockers plus the P1 exposure/role-independence control are closed. No additional recipients are authorized. See `evidence-scope-status-2026-09-03.md`, `email-interview-fieldwork-pack.md`, and the benchmark README for the controlled workflow.

## Nebius Token Factory mode

Copy `.env.example` to `.env` only after a live run has been explicitly authorized. Set `NEBIUS_API_KEY`, current input/output prices, a hard `NEBIUS_MAX_COST_USD`, and the exact one-use confirmation shown in the harness documentation; then launch with `AGROFIELD_PROVIDER=nebius`. The default model is `nvidia/nemotron-3-super-120b-a12b`; it can be changed with `NEBIUS_MODEL`.

The application routes Nebius mode through the guarded OpenAI-compatible adapter. It disables Nemotron reasoning for this extraction step, forces a tool call with a closed schema, revalidates its exact argument shape, validates literal evidence, requires usage telemetry, disables automatic retries, and permits at most one request per process. It refuses to start if confirmation, prices, cap, or key are absent. No key is ever sent to the browser.

```bash
set AGROFIELD_PROVIDER=nebius
set NEBIUS_API_KEY=...
set NEBIUS_INPUT_PRICE_PER_MILLION=...
set NEBIUS_OUTPUT_PRICE_PER_MILLION=...
set NEBIUS_MAX_COST_USD=...
set AGROFIELD_NEBIUS_LIVE_CONFIRMATION=RUN_ONE_NEBIUS_REQUEST
python -m agrofield_agent
```

No live Nebius or Tavily request is made by the default configuration.

Before any future authorized API smoke, run the network-free cost and contract preflight. This command deliberately exits with code 2 because it omits the one-use live confirmation:

```bash
python -m agrofield_agent.nebius_smoke \
  --note-file fixtures/nebius_smoke_note.txt \
  --input-price-per-million 0.06 \
  --output-price-per-million 0.24 \
  --max-cost-usd 0.01
```

The prices above are only the values observed for Nemotron Nano on 2026-09-14 and must be rechecked before use. The harness sends no retries, rejects empty or nonliteral output, emits only sanitized failure diagnostics, and requires fresh human authorization plus an exact live-confirmation phrase. A single live `/api/analyze` attempt reached an upstream HTTP/transport failure before the tool contract could be evaluated; no model inference or output was proven. See [`docs/submission/nebius-api-compatibility-harness.md`](docs/submission/nebius-api-compatibility-harness.md).

## Tavily policy

Tavily is not used to invent a diagnosis. It is called only when a recent external alert could change **where or when to inspect**, and results are limited to configured authoritative domains such as INTA, SMN, SENASA, and university extension sites. Retrieved sources are displayed with date and URL, and never bypass the evidence gate.

## Repository map

```text
src/agrofield_agent/   application, providers, policy, storage, UI
fixtures/              demo data and annotated evaluation cases
benchmark/             blind-review protocol, candidates, templates, reports
tests/                 unit and API tests
docs/research/         frozen rules and competitive research
docs/evaluation/       metric definitions and acceptance gates
docs/architecture.md   system design and trust boundaries
docs/submission/       local Devpost draft, demo runbook, and claim controls
```

All demo locations are synthetic. Exact field coordinates are not stored; `0.0, 0.0` is a deliberate non-location sentinel required by the current application schema.

## Submission status

This repository is local and has not been published, deployed, or submitted. The judge-facing copy and recording plan are prepared under `docs/submission/`, but a public URL, public repository, YouTube video, and Devpost submission still require explicit user authorization.

On 2026-09-14, one separately authorized Playground inference ran on Nebius Token Factory with `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`. Connectivity passed, but the 256-token reasoning budget ended before a final JSON message, so the structured-output smoke test failed. This is real runtime evidence, not an application integration or benchmark result. No personal charge appeared, the post-trial preference was set to stop usage, and the temporary API key was revoked. See `docs/submission/nebius-smoke-run-2026-09-14.md`.

Later that day, a second, separately authorized request ran from AgroField's guarded
repository harness with one request, zero retries, and a US$0.01 promotional-credit
cap. The preflight ceiling was US$0.00122880. API connectivity passed, but the model
did not return exactly one tool call, so the strict contract rejected the response.
The temporary key was revoked and the API-key list was verified empty. This is not a
successful extraction, a live `/api/analyze` result, or a benchmark. See
`docs/submission/nebius-api-smoke-run-2026-09-14.md`.

After that run, the request contract was hardened locally in commit `911d786`: Nano
reasoning is disabled explicitly, the function schema is closed and fully required,
and failures preserve only safe response-shape diagnostics.

A third, separately authorized attempt then exercised the real `/api/analyze` route
with one request, zero retries, the same US$0.01 promotional cap, and Tavily off. The
local route returned HTTP 503 after an upstream HTTP/transport failure. The running
adapter version did not preserve the upstream status, so model invocation cannot be
proven and no tool contract or extraction was evaluated. The temporary key was
revoked and the key list was verified empty. See
`docs/submission/nebius-live-route-smoke-run-2026-09-14.md`.

Commit `e8a926a` subsequently added safe upstream status/request-ID diagnostics and
removed two optional JSON Schema keywords while retaining equivalent client-side
validation. This change is locally tested only and is not a successful Nemotron
result. A further documentation audit found that the raw `httpx` request had
serialized the OpenAI SDK helper name `extra_body` instead of merging
`chat_template_kwargs` into the JSON root. Commit `e0f0ad2` corrects the wire format;
68/68 local tests pass, but the correction has not been sent to Nebius. See
`docs/submission/nebius-wire-format-correction-2026-09-14.md`.

## License

MIT. See [LICENSE](LICENSE).
