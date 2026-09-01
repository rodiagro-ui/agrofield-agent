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
- [x] Human-validation authorization, recruitment, consent, privacy, role, and execution packet prepared with status `NOT_AUTHORIZED`.
- [x] Preflight risks in blind-packet separation and evaluator readiness documented before human review.
- [x] Five P0 preflight blockers closed: separate Phase A/B, strict forms, primary-only task precision, complete double-output review, and exhaustive validation gates.
- [x] Gate contract covered by 41 local tests, including per-gate negatives and an explicitly non-evidentiary 30/10 positive fixture.

## Requires user authorization or external validation

- [ ] Register/verify Builder Program and Token Factory accounts.
- [ ] Confirm credits actually issued and freeze authenticated model prices.
- [ ] Run the annotated suite on Nemotron Nano and Super under an approved cap.
- [ ] Interview 3–5 Argentine advisers with consent and revise the workflow.
- [ ] Have an agronomist review all 30 cases, double-annotate the fixed 10, and adjudicate disagreements.
- [ ] Receive explicit authorization for human outreach; P0 technical findings are already closed.
- [ ] Obtain human labels for every proposed task and reach task precision ≥0.90.
- [ ] Freeze the final human-reviewed benchmark; all current freezes remain candidate-only and `benchmark_validated: false`.
- [ ] Choose a deployment host and approve a spend ceiling.
- [ ] Deploy a public demo and add monitoring through the judging period.
- [ ] Create and make the repository public.
- [ ] Record and publish a sub-three-minute YouTube demo in English or with English translation.
- [ ] Complete and submit Devpost before 2026-10-30 10:00 PDT / 14:00 ART.

## Go/no-go gates

Do not publish if `benchmark_validated` is false, critical-omission recall is below 0.98, any task can be approved without a named reviewer, the live demo lacks a runtime Nemotron call, or the cost/availability plan cannot keep the demo accessible through judging.
