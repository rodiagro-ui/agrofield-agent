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
- [x] Gate contract covered by 44 local tests, including per-gate negatives and an explicitly non-evidentiary 30/10 positive fixture.
- [x] Local submission workspace with English Devpost copy, a timed demo runbook, and explicit truth/authorization gates.
- [x] One sanitized first-party workflow account recorded as non-independent founder domain input; it is not counted as external validation.

## Requires user authorization or external validation

- [ ] Register/verify Builder Program and Token Factory accounts.
- [ ] Obtain a card-free Token Factory access path or already-issued promotional project; the 2026-09-08 attempt stopped before inference because onboarding required a card.
- [ ] Confirm credits actually issued and freeze authenticated model prices.
- [ ] Run the annotated suite on Nemotron Nano and Super under an approved cap.
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
