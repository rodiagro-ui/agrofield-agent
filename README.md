# AgroField Agent

[![ci](https://github.com/rodiagro-ui/agrofield-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/rodiagro-ui/agrofield-agent/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

AgroField Agent is a protocol-aware field-scouting coordinator for soybean fields after heavy rain, wind, or hail. It turns a spoken or typed field note, weather context, and field history into a structured evidence packet, highlights what still needs to be checked, ranks follow-up work, and requires human approval before creating a decision.

**Demo video (2 min):** https://youtu.be/btm73c6GPyY

**Live demo:** https://agrofield-agent.onrender.com/?lang=en (free instance: the first load after idle takes about a minute; every analysis is a real, capped Nemotron 3 Super call through Nebius Token Factory).

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
- Append-only application audit events stored in SQLite.
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

The application routes Nebius mode through the guarded OpenAI-compatible adapter. It disables Nemotron reasoning for this extraction step, forces a tool call with a closed schema, and asks the model to select source IDs from exact input fragments. The application resolves those IDs to original quotes, revalidates argument shape and literal evidence, requires usage telemetry, disables automatic retries, and permits at most one request per process. It refuses to start if confirmation, prices, cap, or key are absent. Application responses never expose provider credentials. Literal provenance does not guarantee that a selected value is supported by its quote.

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

### Public demo mode (not enabled by default)

`AGROFIELD_PROVIDER=nebius-demo` serves many notes for judges while keeping every
guard of the single-request contract (one POST per note, zero retries, closed
schema, literal evidence). It adds a persistent SQLite spend ledger with a hard
total budget, a daily request cap and a per-minute rate limit, all enforced
before any network access. It refuses to start unless `AGROFIELD_NEBIUS_DEMO_CONFIRMATION`,
both prices, `NEBIUS_MAX_COST_USD` and `AGROFIELD_DEMO_TOTAL_BUDGET_USD` are set
(see `.env.example`). When the budget is exhausted `/api/analyze` returns HTTP 429
and the interface says so; only an explicit `?engine=local` request answers with the
local extractor, and its telemetry names that engine. `GET /api/runtime` reports the
engine and the ledger without credentials. The ledger is an application estimate
from reported tokens, not an invoice; the account-level usage stop on Token Factory
remains the real backstop. This mode has **not** been exercised live yet.

### Optional second-pass support verifier

Literal quotes prove provenance, not entailment. With `AGROFIELD_VERIFIER_MODEL`
set (for example `nvidia/nemotron-3-super-120b-a12b`, with its own
`NEBIUS_VERIFIER_*_PRICE_PER_MILLION`), demo mode makes one more guarded Nemotron
call per note that judges, field by field, whether the quote supports the
extracted value, unit and scope. Fields judged unsupported or ambiguous are
cleared to null/unknown and listed as uncertainties before deterministic policy
runs, so a doubtful value becomes a follow-up question instead of a fact. The
verifier can remove values, never add them; if it fails, the extraction is kept
and labeled unverified. The response carries a `verification` object, the audit
trail records an `observation_verified` event, and the interface shows the
badge. Each verification is admitted by the same spend ledger. Profile
`support-judge-es-v1-candidate` has not been evaluated live.

The interface is bilingual: field notes stay in Spanish, and the chrome,
completeness questions and task templates switch to English with the `EN` button
or `?lang=en`, without touching `policy.py`.

### Single-use browser handoff and capped batch evaluation

`python -m agrofield_agent.handoff_runner` rehearses the full browser → loopback →
`/api/analyze` path with a simulated transport and a fixed fictitious value; its
`--mode live` variant performs the one authorized request from a key pasted into a
local form. See `docs/submission/handoff-rehearsal-2026-10-09.md`.

`python -m agrofield_agent.nebius_eval` runs synthetic development notes through
the guarded contract under a total cap and a request count, one request per note
and zero retries, and compares all 12 fields with the local extractor on the same
cases. Without `--confirm-live RUN_NEBIUS_EVAL_BATCH` it prints the plan and exits
2. It refuses holdout cases. Its output is a development diagnostic on synthetic
references, never a validated benchmark. No batch has been run yet.

Before any future authorized API smoke, run the network-free cost and contract preflight. This command deliberately exits with code 2 because it omits the one-use live confirmation:

```bash
python -m agrofield_agent.nebius_smoke \
  --note-file fixtures/nebius_smoke_note.txt \
  --input-price-per-million 0.06 \
  --output-price-per-million 0.24 \
  --max-cost-usd 0.01
```

The prices above were observed for Nemotron Nano on 2026-09-14 and rechecked on 2026-09-15; recheck before every use. The harness sends no retries, rejects empty or nonliteral output, emits only sanitized failure diagnostics, and requires human authorization plus an exact live-confirmation phrase. Four historical single-request authorizations were consumed. A new authorized attempt was paused before inference on September 15 due to a local handoff failure; it is not permission to retry automatically. See the [pause record](docs/submission/nebius-semantic-preflight-pause-2026-09-15.md) and [guarded harness](docs/submission/nebius-api-compatibility-harness.md).

Audit the first accepted real response **offline**, without provider credentials:

```bash
python -m agrofield_agent.smoke_audit
```

This compares a saved Nemotron response and current local extraction against one developer-authored synthetic reference. It is not a blind benchmark: Nemotron got four of eight expected observed fields right, omitted three, misclassified the event, and added an unsupported general condition. The local extractor got eight of eight observed fields right on this one development note. See the [full adverse result](docs/submission/nebius-source-anchor-run-2026-09-14.md).

The current extraction profile is `source-anchors-es-v2-semantic-candidate`: explicit field definitions, distinctions between times/percentages, and client-side rejection of negative or nonfinite quantities. It has **not been evaluated live**. Twenty separate AI-authored synthetic development cases and their request budgets can be checked without network access:

```bash
python -m agrofield_agent.semantic_preflight
python -m agrofield_agent.freeze fixtures/development/semantic_v2/manifest.json --root .
```

These checks validate reference structure and request integrity, not model quality or agronomic correctness. The separate development freeze has 8 files and does not replace the 34-file human-benchmark candidate freeze. See the [v2 candidate report](docs/submission/nebius-semantic-candidate-2026-09-15.md).

## Deploying the public demo

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/rodiagro-ui/agrofield-agent)

`Dockerfile` honors `PORT`; `docker-compose.yml` runs the container locally from a
filled `.env`; `render.yaml` is a Render Blueprint for a free web service with
every non-secret variable preset (Super as extractor and verifier, US$10 total demo
budget, 300 requests per day, 6 per minute). The only secret, `NEBIUS_API_KEY`, is
entered in the host's dashboard. See `docs/submission/deploy-demo.md`.

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
with one request, zero retries, the same US$0.01 promotional cap, and Tavily off.
The local route returned HTTP 503 with `detail: non-literal evidence quote for:
event_type`; the tool contract did not pass because the `event_type` evidence quote
was not validated as literal. The temporary key was revoked and the key list was
verified empty. See `docs/submission/nebius-live-route-smoke-run-2026-09-14.md`.

Commit `e8a926a` subsequently added safe upstream status/request-ID diagnostics and
removed two optional JSON Schema keywords while retaining equivalent client-side
validation. This change is locally tested only and is not a successful Nemotron
result. A further documentation audit found that the raw `httpx` request had
serialized the OpenAI SDK helper name `extra_body` instead of merging
`chat_template_kwargs` into the JSON root. Commit `e0f0ad2` corrects the wire format;
68/68 local tests passed at that historical checkpoint. See
`docs/submission/nebius-wire-format-correction-2026-09-14.md`.

After source-ID anchoring in `1c432ed`, a fourth separately authorized request
returned the first accepted `ObservationDraft` (HTTP 200). It ran `/api/analyze`
through an in-process FastAPI TestClient with real Nebius HTTPS, not a public
deployment. Usage was 2,288 input / 311 output tokens, latency 7.59 seconds and
estimated cost US$0.00021192. The policy remained blocked and one proposed task
remained pending. The key was revoked. The format contract passed, but the
single-note quality audit failed; no Nemotron benchmark or superiority has been
established. The [run record](docs/submission/nebius-source-anchor-run-2026-09-14.md)
preserves those limitations. Current local verification: **184 tests passing**,
34/34 frozen hashes unchanged, zero independent human reviews.

On 2026-10-09 the complete browser-to-route handoff was rehearsed with a simulated
transport and a fictitious value; no key was created and no inference ran. The
public demo mode, the capped batch evaluator and the bilingual interface were added
the same day and are tested locally only.

On 2026-10-10 the single authorized request ran through that complete path with a
real temporary key pasted by the owner into the local single-use form: HTTP 200,
2.37 s, 3,259/290 tokens, estimated US$0.00026514, and **12/12 fields** against the
fixed synthetic reference under the v2 profile (the 2026-09-14 run scored 4/8). One
development note, not a benchmark. See
`docs/submission/nebius-live-handoff-run-2026-10-10.md`.

Later the same day, capped batches ran the 20 synthetic development notes through
the guarded contract. Under profile v3, **Nemotron 3 Super** accepted 18/20 notes
with micro-F1 **0.934** (precision 0.955, recall 0.914, 15/20 notes fully right,
p95 2.7 s, about US$0.0014 per note); Nano accepted 10/20 with F1 0.65; the local
extractor scores 0.82 on the same notes. Super is therefore the demo model. These
are AI-authored synthetic references, not a validated benchmark. See
`docs/submission/nebius-batch-v3-nano-super-2026-10-10.md`.

## License

MIT. See [LICENSE](LICENSE).


