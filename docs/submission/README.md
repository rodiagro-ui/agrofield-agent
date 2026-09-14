# AgroField Agent submission workspace

> Local preparation only. Do not publish, deploy, upload, or submit any artifact in this directory without a separate explicit authorization from the project owner.

This directory contains the judge-facing narrative and demo plan for the Nebius x NVIDIA Global AI Hackathon 2026. It is intentionally outside the frozen blind-benchmark package.

## Current positioning

**AgroField Agent turns an incomplete post-storm soybean scouting note into traceable evidence, explicit missing checks, prioritized follow-up work, and human-approved decisions.**

The project should compete on a narrow operational failure: a plausible field message can look complete while omitting the measurements required to act safely. It should not be presented as a generic agronomy chatbot or an autonomous prescriber.

## Artifact map

- `devpost-draft.md`: English submission copy with unresolved fields clearly marked.
- `demo-runbook.md`: sub-three-minute recording plan and retake criteria.
- `founder-domain-input-2026-09-08.md`: sanitized, non-independent product-discovery evidence.
- `strategy-decision-2026-09-08.md`: decision to proceed without waiting for the full 30/10 human benchmark.
- `rules-recheck-2026-09-08.md`: current official requirements and judging implications.
- `nebius-smoke-attempt-2026-09-08.md`: stopped pre-inference attempt and zero-cost evidence.
- `card-free-access-request.md`: exact support request and the later support outcome.
- `nebius-smoke-run-2026-09-14.md`: one real Nemotron Playground request, its adverse empty-output result, authenticated pricing, billing controls, and credential revocation.
- `nebius-api-compatibility-harness.md`: strict one-request contract shared by the CLI harness and guarded application provider.
- `nebius-api-smoke-run-2026-09-14.md`: one real request from AgroField's guarded harness, its adverse missing-tool-call result, cost preflight, and credential cleanup.
- `nebius-tool-contract-hardening-2026-09-14.md`: local-only reasoning/schema/diagnostic hardening after the adverse request; not live-validated.
- `nebius-live-route-smoke-run-2026-09-14.md`: the separately authorized live `/api/analyze` attempt, its evidence-contract failure (`non-literal event_type`), strict claim boundary, and cleanup evidence.
- `nebius-wire-format-correction-2026-09-14.md`: local correction of the SDK-vs-raw `extra_body` serialization error and its evidence boundary.

## Truthful status

| Item | Current status |
|---|---|
| Local vertical MVP | Functional |
| Local tests | 68/68 passing on 2026-09-14, including 23 mocked guarded-Nebius tests |
| Safe recording rehearsal | Verified end to end with fresh temporary data and explicit local/synthetic label |
| Local 12-case regression baseline | F1 0.9551; critical-omission recall 1.0000 |
| Local 30-case candidate | F1 0.9188; critical-omission recall 0.9714 |
| Independent human validation | Not completed |
| `benchmark_validated` | `false` |
| Real Nemotron runtime | Three separately authorized request attempts ran on 2026-09-14; only Playground proves model execution, none produced an accepted extraction, and no benchmark ran |
| AgroField API integration / Nemotron evaluation | The guarded CLI reached the live API once; a separate `/api/analyze` attempt returned HTTP 503 with strict evidence contract failure (`non-literal event_type`) and no `ObservationDraft`; no Nemotron evaluation has run |
| Current compatibility candidate | Raw `httpx` now sends top-level `chat_template_kwargs`; 68/68 local tests pass, but the correction is not live-validated |
| Card-free access request | Support confirmed that no card-free activation path is available |
| Tavily runtime evidence | Not run |
| Public repository, URL, video, submission | Not created |

All evaluation numbers above use `local/deterministic-es-v0.1` and synthetic cases. They are neither Nemotron results nor agronomist-validated evidence.

## Path to a valid entry

1. Keep the verified local rehearsal and judge-facing copy synchronized without presenting it as a Nemotron run.
2. Preserve the locally hardened compatibility candidate and do not describe its tool contract as live-validated.
3. Obtain separate authorization and a hard spending limit before any additional Nebius or Tavily call; all three existing authorizations are consumed.
4. Only after the contract passes, consider a separately capped frozen-suite evaluation.
5. Replace every placeholder in the submission and demo with measured values.
6. Decide whether Tavily earns demo time through a documented ablation; omit it if it does not.
7. Request separate authorization before repository publication, deployment, video upload, or Devpost submission.

The full 30-primary/10-double human benchmark remains the gold-standard research target. It is not weakened or relabeled by the lean submission strategy.
