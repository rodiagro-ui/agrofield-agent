# AgroField Agent — Devpost draft

> **DO NOT PUBLISH YET.** Replace every `TBD` item with verified evidence. Publication and submission require separate owner authorization.

## Project title

AgroField Agent

## Tagline

Evidence before action after the storm.

## Elevator pitch

AgroField Agent is a protocol-aware operations agent for post-storm soybean scouting. It converts a spoken or typed field note into traceable structured observations, identifies the critical checks that were not reported, prioritizes follow-up work across fields, and keeps every consequential task pending until a named human reviews it.

It is not an autonomous agronomist. Its core job is to stop an incomplete but plausible message from becoming an unsafe decision.

## The problem

After heavy rain, hail, or wind, advisers may receive fragmented messages from several fields while weather conditions and access constraints are still changing. Those notes often sound decisive even when they do not establish crop stage, event timing, safe access, representative sampling, affected area, water duration, or plant damage.

A first-party workflow account from the project owner reinforced three design requirements: check transitability before agronomy, inspect multiple representative points instead of judging from the entrance, and delay irreversible decisions until recovery can be observed. This input is non-independent and is presented as product discovery, not market validation.

## What it does

1. Captures a Spanish field note by text or browser speech recognition.
2. Uses NVIDIA Nemotron through Nebius Token Factory for constrained extraction, intended to retain only supported observations; current extraction-quality limitations are disclosed below.
3. Attaches a literal evidence quote to each extracted value.
4. Applies deterministic rules to identify missing critical checks for flooding, hail, wind, or mixed events.
5. Combines the note with synthetic field history and weather context to explain inspection priority.
6. Proposes follow-up tasks without executing them.
7. Requires a named human to approve or reject each task and records the decision in an append-only audit trail.

Optional Tavily retrieval is restricted to recent allowlisted official sources. It may change where or when to inspect, but it cannot establish what exists inside a field or authorize treatment.

## Why this is different

Most agriculture assistants optimize for producing an answer. AgroField optimizes for proving whether the observation is sufficient to support the next operational step.

The visible red state — “decision blocked; critical checks missing” — is not an error screen. It is the product. The language model extracts and summarizes evidence; deterministic application code owns completeness, severity, and approval controls.

## Demo story

Target narrative, verified in the local/synthetic rehearsal and, on 2026-10-09, in a full browser → server → `/api/analyze` rehearsal with a simulated Nemotron transport. The complete live Nemotron browser workflow still needs verification.

The interface is bilingual: scouts write notes in Spanish, and judges can switch the interface, completeness questions and task templates to English with the `EN` button or `?lang=en`.

An incomplete note reports soybean stage, a recent storm, safe access, standing water, and a low stand in one area. AgroField preserves those facts but blocks closure because the note does not report representative sampling or water duration. It asks only the missing questions.

The user then supplies a complete note with a W-shaped route, multiple sampling points, affected area, and water duration. The evidence becomes ready for review, a follow-up visit is proposed, and the task remains pending until a named adviser approves it. The audit panel shows the observation, proposal, and human decision.

## Architecture

- Mobile-first web interface and browser voice capture.
- FastAPI orchestration layer.
- NVIDIA Nemotron through Nebius Token Factory using an OpenAI-compatible, schema-constrained tool call.
- Pure deterministic evidence and safety policy.
- SQLite field memory, proposed tasks, approvals, and audit events.
- Optional Tavily adapter with domain allowlists and retained source URLs.

The public demo runs Nemotron through a budgeted provider: every note is one guarded request with zero retries, admitted first by a persistent spend ledger with a hard total budget, a daily cap and a per-minute limit. When the budget is exhausted the interface says so and only an explicitly labeled local extractor answers; it is never a silent fallback. `GET /api/runtime` shows the engine and the remaining budget without credentials.

Application responses never expose provider credentials. Structurally invalid model output is rejected. Missing required evidence produces a blocked state. Exact quotes do not guarantee semantic correctness: the first accepted smoke still contained an unsupported value, so this is not a guarantee against all model errors.

## Current evidence — replace before submission

| Evaluation | Provider | Cases | F1 | Critical-omission recall | Unsupported assertion rate | Decision safety |
|---|---|---:|---:|---:|---:|---:|
| Local regression suite | `local/deterministic-es-v0.1` | 12 synthetic | 0.9551 | 1.0000 | 0.0000 | 1.0000 |
| Hard candidate suite | `local/deterministic-es-v0.1` | 30 synthetic | 0.9188 | 0.9714 | 0.0050 | 1.0000 |
| Nemotron | `TBD_AFTER_AUTHORIZED_RUN` | TBD | TBD | TBD | TBD | TBD |

Four separately authorized requests used `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`: the Playground exhausted its reasoning budget without a final message; the guarded CLI failed the exactly-one-tool-call contract; the third request reached local evidence validation but was rejected for a nonliteral `event_type` quote (not a connection failure); the fourth produced the first accepted observation with HTTP 200 through in-process `/api/analyze` and real Nebius HTTPS.

That fourth response took 7.59 seconds, reported 2,288 input / 311 output tokens, and cost an estimated US$0.00021192 at the observed rates. Against one synthetic developer reference it correctly extracted only four of eight expected observed fields, omitted three, misclassified the event, and asserted an unsupported general condition. Local extraction got eight of eight observed fields right on that same note. These are a single-case development diagnostic, not a held-out benchmark, and do not replace the `TBD` row above. All nonempty quotes were literal; semantic support still failed. See `nebius-source-anchor-run-2026-09-14.md` and its network-free audit.

The 30-case candidate remains `benchmark_validated: false` and contains no independent human labels. The local numbers must never be described as Nemotron performance.

## Built with

Python, FastAPI, Pydantic, SQLite, vanilla JavaScript, HTML/CSS, NVIDIA Nemotron, Nebius Token Factory, and optionally Tavily.

## Challenges

- Separating an LLM's extraction role from deterministic safety authority.
- Preserving exact evidence provenance while normalizing field measurements.
- Making missing information visible without turning the workflow into a long form.
- Designing evaluation that reports adverse failures instead of hiding them behind an aggregate score.
- Planning a credible live-model evaluation under strict cost and privacy constraints.

## Accomplishments

- A functional vertical workflow rather than a general chatbot.
- Explicit evidence quotes and event-specific completeness rules.
- Human approval and auditability implemented end to end.
- Reproducible synthetic evaluations with an E1–E8 failure ledger.
- A prepared Nemotron adapter that cannot bypass deterministic policy.
- A source-restricted Tavily integration that fails safely when unavailable.

## What we learned

In a high-consequence workflow, fluency is not the same as readiness. The useful boundary is not “Can the model answer?” but “What did the field note establish, what remains unknown, and who is accountable for the next step?”

## What's next

- Verify the locally prepared semantic v2 candidate with a separately authorized, capped live comparison. Twenty AI-authored development references and improved field instructions are ready; mocks/reference checks alone do not demonstrate model quality gains.
- Only then consider the frozen suites on Nemotron under a separately approved cap.
- Measure quality, p95 latency, tokens, retries, and cost per completed visit.
- Complete independent agronomy review without changing the frozen references after seeing holdout results.
- Keep Tavily only if an ablation shows a measurable improvement in inspection prioritization.
- Harden the public deployment, privacy notice, and uptime monitoring for judging.

## Testing instructions for judges

Draft for a future authorized public deployment, not currently live or end-to-end verified with Nemotron.

1. Open `TBD_PUBLIC_URL?lang=en` (the `EN` button switches languages at any time; field notes stay in Spanish, the scouts' language).
2. Confirm the header badge displays `Nemotron · Token Factory`; `TBD_PUBLIC_URL/api/runtime` shows the model and the remaining demo budget.
3. Select **Lote Bajo** and choose **Incomplete note**.
4. Click **Analyze evidence** and verify literal evidence quotes plus a blocked state with two missing checks.
5. Choose **Complete note**, analyze again, and verify the review-ready state and proposed tasks.
6. Enter a reviewer label and approve one proposed task.
7. Open **Audit trail** and verify the recorded observation, proposal, and human decision.
8. Optional: paste your own Spanish note; every analysis is one capped Nemotron request. If the demo budget is exhausted, the interface says so and labels the local extractor's result.

Demo data and locations are synthetic. No treatment is autonomously recommended or executed.

## Nebius and NVIDIA feedback

Initial real-use evidence: Token Factory exposed model choice, token pricing and Playground timing. Early requests revealed reasoning-budget and output-contract failures. Source-ID anchoring subsequently produced one accepted observation with usage telemetry, but semantic extraction remained worse than local extraction on the single development note. Tool compatibility and quote provenance are separate from quality; aggregate Nemotron benchmark performance remains unmeasured.

## Required links

- Live application: `TBD_PUBLIC_URL`
- Public repository: `TBD_PUBLIC_REPOSITORY`
- Video under three minutes: `TBD_PUBLIC_YOUTUBE_URL`
- License: MIT

## Tavily bonus decision

`PENDING_ABLATION`. Do not claim the bonus integration merely because an adapter exists. Demonstrate a recent official alert changing inspection priority with its date and URL, measure the incremental value, and show that the alert does not assert field presence. Otherwise omit Tavily from the final pitch.
