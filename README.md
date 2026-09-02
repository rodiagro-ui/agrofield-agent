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

Run tests and the evaluation:

```bash
pytest
python -m agrofield_agent.evaluate fixtures/eval_cases.jsonl
```

Run the harder blind-benchmark candidate:

```bash
python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl
```

The 30-case set is synthetic and currently has **zero human agronomy reviews and zero real interviews**. One interview invitation has been sent; no acceptance or evidence has been recorded. Its output is labeled `provisional_candidate_reference`; it is not a Nemotron result or agronomist-validated evidence. All five P0 blockers plus the P1 exposure/role-independence control are closed. The private setup has been attested without adding PII to Git; the user may now send the remaining email-only invitations within the approved caps. See `benchmark/agronomy_blind_v1/authorization/outreach-status-2026-09-02.md`, the email pack, and the benchmark README for the controlled workflow.

## Nebius Token Factory mode

Copy `.env.example` to `.env`, set `NEBIUS_API_KEY`, and launch with `AGROFIELD_PROVIDER=nebius`. The default model is `nvidia/nemotron-3-super-120b-a12b`; it can be changed with `NEBIUS_MODEL`.

The adapter uses Nebius's OpenAI-compatible chat completions API and forces a tool call whose arguments match the observation schema. No key is ever sent to the browser.

```bash
set AGROFIELD_PROVIDER=nebius
set NEBIUS_API_KEY=...
python -m agrofield_agent
```

No live Nebius or Tavily request is made by the default configuration.

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
```

All demo locations are synthetic. Exact field coordinates are not stored; `0.0, 0.0` is a deliberate non-location sentinel required by the current application schema.

## Submission status

This repository is local and has not been published, deployed, or submitted. A public URL, public repository, YouTube video, and Devpost submission still require explicit user authorization.

## License

MIT. See [LICENSE](LICENSE).
