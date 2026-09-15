# Submission readiness

## Completed locally

- [x] Narrow, non-chatbot workflow selected.
- [x] Architecture with explicit trust boundaries.
- [x] Local mobile-first MVP.
- [x] Nemotron Token Factory adapter.
- [x] Optional, source-restricted Tavily adapter.
- [x] Persistent lot memory and audit events in SQLite.
- [x] Human approval before task decisions.
- [x] Annotated synthetic evaluation fixtures and baseline.
- [x] Blind-benchmark protocol, consent, anonymization, rubric, and review forms.
- [x] Thirty-case candidate set with a 20/10 split and 10 fixed double-review cases.
- [x] Extended evaluator for task precision, E1–E8, adverse failures, reviewer agreement, and readiness gates.
- [x] Candidate privacy pass with real coordinates removed or replaced by an explicit non-location sentinel.
- [x] Open-source license, README, container definition, and secret hygiene.
- [x] Significant-work changelog dated after 2026-08-26.
- [x] Human-validation outreach authorized for user-sent email only, with explicit 5 + 3 caps, no recording/compensation, private custody, and no authorization for paid/public actions.
- [x] Preflight risks in blind-packet separation and evaluator readiness documented before human review.
- [x] Five P0 preflight blockers closed: separate Phase A/B, strict forms, primary-only task precision, complete double-output review, and exhaustive validation gates.
- [x] P1 closed: binding agreement keeps every complete pair, exposure sensitivity is separate, and global reviewer/adjudicator role overlap blocks readiness.
- [x] Core application and benchmark contract covered by local tests, including per-gate negatives and an explicitly non-evidentiary 30/10 positive fixture.
- [x] Local submission workspace with English Devpost copy, a timed demo runbook, and explicit truth/authorization gates.
- [x] One sanitized first-party workflow account recorded as non-independent founder domain input; it is not counted as external validation.
- [x] Network-free Nebius compatibility harness wired into the application with hard cost preflight, exact one-request confirmation, one-request-per-process enforcement, no retries, sanitized diagnostics, closed-schema and literal-evidence checks, telemetry requirements, and 37 mocked tests.
- [x] Post-failure compatibility profile hardened locally: reasoning explicitly disabled, strict defaults removed, exact argument shape revalidated, and budget-exhaustion diagnostics classified without retaining model text.
- [x] Live-route failure hardened locally: future upstream failures preserve only status, safe request ID and latency; optional schema keywords were removed while equivalent client-side validation remains.
- [x] Raw wire format corrected locally: `chat_template_kwargs` is top-level for direct `httpx`; the OpenAI SDK-only `extra_body` wrapper is no longer serialized.
- [x] Shared Token Factory base URL aligned with the current official API documentation.
- [x] Model-selected source IDs resolved to exact original-note excerpts, with nine source-span tests; this verifies provenance, not semantic support.
- [x] Offline audit of the first accepted live response with three regression tests: all 12 fields examined, adverse errors preserved, no network calls.
- [x] Current local suite: 124 tests passing; human-benchmark candidate freeze 34/34 unchanged.
- [x] Semantic v2 profile: explicit field meanings and nonnegative/finite numeric guards; 20 separate AI-authored synthetic development cases, 30 reference/profile tests and an 8-file development freeze. No live v2 evaluation or human validation implied.

## Requires user authorization or external validation

- [x] Authenticate and complete Token Factory trial onboarding.
- [x] Receive the official card-free answer: support confirmed that a payment method is required and no card-free hackathon path is available.
- [x] Set the post-trial preference to `Stop usage` before the first inference.
- [x] Freeze authenticated Nano public-endpoint prices observed on 2026-09-14: US$0.06/M input and US$0.24/M output.
- [x] Run one authorized real Nemotron Playground smoke test; connectivity passed but the structured final output failed because the 256-token budget ended during reasoning.
- [x] Revoke the temporary API key after its value became visible to the automation session; the API-key list was verified empty.
- [x] Run one separately authorized guarded AgroField-harness API smoke with a US$0.01 promotional cap and zero retries; connectivity passed, the exactly-one-tool-call contract failed, and the key was revoked.
- [x] Exercise the real `/api/analyze` path once under a separate cap; it sent one request, returned HTTP 503, and failed strict contract validation with `non-literal evidence quote for: event_type`, so the tool contract did not pass.
- [x] First accepted `ObservationDraft` from real Nebius through `/api/analyze` in-process TestClient, HTTP 200; fourth separately authorized inference, one request and zero retries. See `submission/nebius-source-anchor-run-2026-09-14.md`.
- [ ] Acceptable extraction quality: the first accepted response got only 4/8 expected observed fields right on one synthetic development note and added an unsupported condition; literal quotes alone did not ensure correctness.
- [ ] Live browser-to-server Nemotron demo with both incomplete and complete notes; the accepted in-process smoke does not establish this.
- [ ] Run the annotated suite on Nemotron Nano and Super under a separately approved cap.
- [x] User attested that the private privacy addendum, storage/retention/rights channel, recipient selection, and coded role map are complete without adding PII to Git.
- [x] User reports all authorized outreach sent: 5/5 interview invitations and 3/3 reviewer invitations. No additional recipients are authorized.
- [x] User reports preliminary verbal acceptance from all five interview candidates and preliminary verbal coverage of `R01`, `R02`, and `A01`.
- [x] User attests that separate mandatory written consents are privately retained and valid for 5/5 interviews and `R01`, `R02`, and `A01`; no PII or raw response entered Git/AI.
- [x] User attests evaluator-required scopes: 5/5 aggregate insights, 5/5 sanitized scenarios, and anonymous/aggregated results for `R01`, `R02`, and `A01`; recording remains 0/8.
- [ ] Interview 3–5 Argentine advisers/producers/scouts with consent and revise the workflow.
- [ ] Three distinct professionals cover `R01`, `R02`, and `A01`: 30 primaries, 10 fixed doubles, and 30 adjudications.
- [ ] Obtain human labels for every proposed task and reach task precision ≥0.90.
- [ ] Freeze the final human-reviewed benchmark; all current freezes remain candidate-only and `benchmark_validated: false`.
- [ ] Choose a deployment host and approve a spend ceiling.
- [ ] Deploy a public demo and add monitoring through the judging period.
- [ ] Create and make the repository public.
- [ ] Record and publish a sub-three-minute YouTube demo in English or with English translation.
- [ ] Complete and submit Devpost before 2026-10-30 10:00 PDT / 14:00 ART.

## Go/no-go gates

`benchmark_validated: false` blocks any claim of independent agronomy validation, but it is not an official hackathon submission requirement. A lean submission may proceed with that limitation disclosed and every synthetic/local number labeled accurately.

Do not publish if any task can execute without a named reviewer, the live demo lacks a runtime Nemotron call, a shown metric is not tied to its provider and dataset, secrets or personal data are exposed, or the cost/availability plan cannot keep the demo accessible through judging. Repository publication, deployment, video upload, and Devpost submission remain separate authorization gates.
