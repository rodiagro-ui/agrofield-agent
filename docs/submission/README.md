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

## Truthful status

| Item | Current status |
|---|---|
| Local vertical MVP | Functional |
| Deterministic local tests | 45/45 passing on 2026-09-09 |
| Safe recording rehearsal | Verified end to end with fresh temporary data and explicit local/synthetic label |
| Local 12-case regression baseline | F1 0.9551; critical-omission recall 1.0000 |
| Local 30-case candidate | F1 0.9188; critical-omission recall 0.9714 |
| Independent human validation | Not completed |
| `benchmark_validated` | `false` |
| Real Nemotron runtime | One Playground request ran on 2026-09-14; connectivity passed, structured final output failed |
| AgroField API integration / Nemotron evaluation | Not run |
| Card-free access request | Support confirmed that no card-free activation path is available |
| Tavily runtime evidence | Not run |
| Public repository, URL, video, submission | Not created |

All evaluation numbers above use `local/deterministic-es-v0.1` and synthetic cases. They are neither Nemotron results nor agronomist-validated evidence.

## Path to a valid entry

1. Keep the verified local rehearsal and judge-facing copy synchronized without presenting it as a Nemotron run.
2. Obtain separate authorization and a hard spending limit before any Nebius or Tavily call.
3. Run a small controlled Nemotron smoke test, then the frozen evaluation if the smoke test is safe and affordable.
4. Replace every placeholder in the submission and demo with measured values.
5. Decide whether Tavily earns demo time through a documented ablation; omit it if it does not.
6. Request separate authorization before repository publication, deployment, video upload, or Devpost submission.

The full 30-primary/10-double human benchmark remains the gold-standard research target. It is not weakened or relabeled by the lean submission strategy.
