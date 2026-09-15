# AgroField Agent submission workspace

> Local preparation only. Publication, deployment, upload and submission require separate explicit owner authorization. Snapshot: 2026-09-15.

## Positioning

AgroField Agent turns an incomplete post-storm soybean scouting note into traceable observations, missing checks, prioritized follow-up work and human-reviewed decisions. It is not an autonomous agronomist or a generic chatbot.

## Truthful status

| Item | Current evidence |
|---|---|
| Local vertical MVP | Functional; safe local/synthetic recording rehearsal verified |
| Local tests | 88 passing, including 31 mocked guarded-Nebius tests |
| Local 12-case baseline | F1 0.9551; omission recall 1.0000 |
| Local 30-case candidate | F1 0.9188; omission recall 0.9714; 53 adverse failures |
| Candidate freeze | 34/34 hashes valid; 7/17 gates; benchmark_validated false |
| Human evidence | Zero independent interviews/reviews; one sanitized non-independent founder input |
| Real Nemotron | Four separately authorized requests; first accepted extraction on request four |
| Accepted route | In-process FastAPI TestClient /api/analyze with real Nebius HTTPS, not public browser E2E |
| Accepted output quality | Only 4/8 expected observed fields right on one synthetic development note; three omissions, one wrong event, one unsupported condition |
| Accepted request telemetry | 7.59 s; 2,288 input / 311 output tokens; estimated US$0.00021192 |
| Aggregate Nemotron benchmark | Not run |
| Credentials and authorization | Temporary key revoked, list verified empty; single-request permissions consumed |
| Tavily | No runtime requests; no measured bonus value |
| Public repository, URL, video, submission | Not created |

The 12/30-case aggregate metrics use local/deterministic-es-v0.1 only. The saved real Nemotron result is a separate one-case development diagnostic, not a held-out score or independent agronomy validation. Immediate rounded billing showed no personal charge; it does not prove zero inference cost.

## Artifact map

- devpost-draft.md: English draft with unresolved links, measured limitations and claim boundaries.
- demo-runbook.md: sub-three-minute local recording plan; the described live demo still needs verification.
- founder-domain-input-2026-09-08.md: sanitized non-independent workflow input.
- strategy-decision-2026-09-08.md: decision to prepare a lean submission without waiting for the full human benchmark.
- rules-recheck-2026-09-08.md: last recorded official-rules recheck, not a new verification on this snapshot date.
- card-free-access-request.md: support outcome; no card-free activation path was offered.
- nebius-smoke-attempt-2026-09-08.md: historical attempt stopped before inference.
- nebius-smoke-run-2026-09-14.md: first actual request, Playground reasoning-budget failure.
- nebius-api-smoke-run-2026-09-14.md: second request, CLI exactly-one-tool-call failure.
- nebius-live-route-smoke-run-2026-09-14.md: third request, nonliteral event_type evidence failure, not a connection failure.
- nebius-api-compatibility-harness.md: current guarded contract and no-network preflight.
- nebius-tool-contract-hardening-2026-09-14.md: historical reasoning/schema changes.
- nebius-wire-format-correction-2026-09-14.md: raw/SDK correction; not a demonstrated cause of earlier failures.
- nebius-source-anchors-2026-09-14.md: local source-ID design and pre-run verification.
- [nebius-source-anchor-run-2026-09-14.md](nebius-source-anchor-run-2026-09-14.md): fourth request, accepted format and adverse quality audit.
- [evidence/nebius-source-anchor-smoke-2026-09-14.json](evidence/nebius-source-anchor-smoke-2026-09-14.json): sanitized accepted response and telemetry.

## Next steps and boundaries

1. Preserve the adverse live response; improve extraction semantics on development cases without changing policy.py or the frozen holdout.
2. Use python -m agrofield_agent.smoke_audit to reproduce the current comparison offline. Mock tests do not prove better live quality.
3. Obtain a new scoped authorization and cost cap before another Nebius or Tavily request. Recheck prices, trial credit and Stop usage immediately before any authorized call.
4. Demonstrate better extraction and the actual browser demo before claiming readiness; run a broader evaluation only under its own approved scope.
5. Complete independent review if available, without representing founder input or synthetic labels as independent evidence.
6. Keep Tavily only if an authorized ablation demonstrates useful, traceable value.
7. Request separate authorization for a public repository, deployment and its operating budget, video upload and Devpost submission.

The full human benchmark remains a credibility target, not a completed requirement. Its gates and frozen references are not weakened by the lean submission strategy.
