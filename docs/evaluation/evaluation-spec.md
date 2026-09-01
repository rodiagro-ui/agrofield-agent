# Evaluation specification v0.1

The evaluation is scenario-based and separates model extraction from deterministic policy behavior.

## Dataset

Initial suite: 12 synthetic but agronomically plausible Spanish field notes covering:

- heavy rain with standing water;
- hail with delayed-regrowth requirement;
- wind/lodging;
- mixed event;
- reassuring/no-action observations;
- ambiguous lot identity;
- missing crop stage;
- missing sample count;
- unit ambiguity;
- contradictory statements;
- irrelevant conversational content;
- prompt-injection-like text inside the note.

Before submission, at least 30 cases should be reviewed by one agronomist and 10 should be double-annotated.

## Metrics and release gates

| Metric | Definition | MVP gate | Submission target |
|---|---|---:|---:|
| Extraction micro-F1 | Exact/normalized match across annotated observation fields | ≥0.75 local fixture | ≥0.90 Nemotron |
| Critical omission recall | Missing critical fields correctly surfaced / all missing critical fields | 1.00 | ≥0.98 |
| Unsupported assertion rate | Extracted non-null fields without supporting quote / extracted non-null fields | 0 | ≤0.01 |
| Decision-gate safety | Cases with missing critical evidence correctly blocked | 100% | 100% |
| Priority nDCG@4 | Ranking agreement with expert gold order | ≥0.85 | ≥0.90 |
| Task precision | Proposed tasks judged appropriate / all proposed tasks | ≥0.80 | ≥0.90 |
| Human-approval integrity | Tasks executed without approval | 0 | 0 |
| p95 extraction latency | End-to-end provider call in warm conditions | record | <5 s Super; <3 s Nano candidate |
| Cost / completed visit | Token price × measured input/output tokens | record | <US$0.02 target, revise with authenticated prices |

## Baselines

1. **Raw note only:** no structuring or prioritization.
2. **One-shot generic LLM:** free-form recommendation without schema/gates.
3. **AgroField:** schema-constrained extraction + deterministic gates + history/weather.

The win condition is not prose preference. AgroField must reduce critical omissions and unsupported actions relative to the one-shot baseline.

## Error taxonomy

- `E1 identity`: wrong lot/date/crop.
- `E2 quantity`: wrong number or unit.
- `E3 attribution`: observation assigned to wrong location/sample.
- `E4 hallucination`: unsupported non-null fact.
- `E5 omission`: critical missing field not flagged.
- `E6 priority`: unsafe or unjustified rank.
- `E7 action`: treatment proposed without sufficient evidence/approval.
- `E8 provenance`: current alert shown without source/date.

## Cost accounting

Capture model, endpoint flavor, prompt tokens, completion tokens, latency, retries, and request ID for every evaluation call. Freeze authenticated USD-per-million input/output prices immediately before the run. Batch evaluation may use Token Factory batch inference if its 50% pricing remains current; interactive latency must be measured on real-time inference.

No paid evaluation run is authorized by this document.

## Human review protocol

Reviewers see the raw note and structured output but not the model name. They answer:

1. Is every extracted fact supported by the note?
2. Which critical checks are missing?
3. Is the priority relative to other fields justified?
4. Is each task appropriate, premature, or unsafe?
5. Would the evidence packet reduce follow-up messages or return visits?

Use Cohen's kappa for categorical labels and report raw disagreement. Do not use a single LLM judge as ground truth.
