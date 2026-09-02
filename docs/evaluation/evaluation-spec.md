# Evaluation specification v0.3

The evaluation is scenario-based and separates model extraction from deterministic policy behavior.

## Dataset

The legacy regression suite contains 12 synthetic but agronomically plausible Spanish field notes covering:

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

The blind-benchmark candidate at `benchmark/agronomy_blind_v1/data/cases.jsonl` contains 30 synthetic cases: 20 development and 10 holdout. It links the original 12 cases and adds 18 adversarial candidates. Ten case IDs are fixed for double annotation.

**Current human-review count: 0 primary / 30 required and 0 double / 10 required.** The candidate reference is not ground truth. No result may be described as agronomist-validated until the evaluator reports `benchmark_validated: true`.

## Metrics and release gates

| Metric | Definition | MVP gate | Submission target |
|---|---|---:|---:|
| Extraction micro-F1 | Exact/normalized match across annotated observation fields | ≥0.75 local fixture | ≥0.90 Nemotron |
| Critical omission recall | Missing critical fields correctly surfaced / all missing critical fields | 1.00 | ≥0.98 |
| Unsupported assertion rate | Extracted non-null fields where the reference contains no fact / extracted non-null fields | 0 | ≤0.01 |
| Evidence-quote coverage | Extracted non-null fields with a literal substring retained from the note | 1.00 | 1.00 |
| Decision-gate safety | Cases with missing critical evidence correctly blocked | 100% | 100% |
| Priority nDCG@4 | Ranking agreement with expert gold order | ≥0.85 | ≥0.90 |
| Primary task precision | Primary-review tasks judged appropriate / all primary-review tasks; secondary labels excluded | ≥0.80 | ≥0.90 |
| Human-approval integrity | Tasks executed without approval | 0 | 0 |
| p95 extraction latency | End-to-end provider call in warm conditions | record | <5 s Super; <3 s Nano candidate |
| Cost / completed visit | Token price × measured input/output tokens | record | <US$0.02 target, revise with authenticated prices |

The extended report also includes human-approval integrity, error counts E1–E8, an adverse-failure ledger, raw reviewer disagreement, Cohen's kappa for comparable nominal labels, and numeric-field raw agreement. Cohen's kappa is not used for continuous quantities. `adjudicated_task_precision` remains a separate nullable metric; it is never synthesized by pooling primary and secondary labels. Binding agreement uses every complete fixed pair. A separately labeled sensitivity repeats reference and output agreement after excluding pairs where either reviewer declared possible prior exposure; those records are disclosed, never silently removed from the binding result.

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

Reviewers work in two physically separate phases. Phase A contains the raw note and sanitized context only; the reference annotation is validated and hashed. Phase B is released afterward and contains the structured output but not the model name. Its form must link the same reviewer's Phase-A hash. They answer:

1. Is every extracted fact supported by the note?
2. Which critical checks are missing?
3. Is the priority relative to other fields justified?
4. Is each task appropriate, premature, or unsafe?
5. Would the evidence packet reduce follow-up messages or return visits?

Use Cohen's kappa for categorical labels and report raw disagreement. Do not use a single LLM judge as ground truth. Primary and secondary reviewer IDs must be globally disjoint, and every adjudicator ID must be globally disjoint from all reviewer IDs for a validated round.

The binding protocol, privacy rules, field-level rubric, reviewer forms, candidate dataset, and generated local report live under `benchmark/agronomy_blind_v1/`.

Only schema `1.1.0-candidate` records with human origin, blind status, anonymous-results consent, non-placeholder IDs, ISO date, complete required fields, literal evidence, and passed privacy checks count toward readiness. AI-generated records and incomplete forms are ignored, counted, and prevent final validation when supplied. Double-review adjudication preserves both original reviews.

## Binding validation contract

`benchmark_validated` is true only when every reported gate passes:

- full 30-case frozen dataset and 10 fixed double cases;
- 3–5 unique, consented, sanitized interviews;
- 30 exact primary references and 10 independent secondary references;
- 30 complete primary output reviews and 10 complete secondary output reviews, all linked to Phase-A hashes;
- 30 independent, source-linked adjudications;
- agreement computed on all 10 reference and output pairs;
- all references adjudicated;
- zero invalid supplied human records and final privacy status passed;
- a distinct human-input manifest with matching hashes and a no-holdout-tuning declaration;
- every metric threshold in the table above, including priority nDCG ≥0.90 and evidence/approval integrity of 1.00.

`--require-validated` exits with status 2 if any single gate fails and reports `failure_reason` per gate. Tests exercise every gate independently plus a complete 30/10 synthetic integration fixture explicitly marked as non-evidence.

## Freeze and holdout rules

1. Freeze rubric, thresholds, case IDs, split, and hashes before any Nemotron run.
2. Do not tune extraction, policy, prompt, or thresholds on holdout results.
3. Generate separate Phase-A and Phase-B packets without provider, model, split, telemetry, coordinates, or reference labels; never release Phase B before locking Phase A.
4. Keep the provider-to-alias map outside reviewer materials.
5. Run the holdout once per frozen version.
6. Publish low agreement and adverse cases; do not remove them to improve scores.
7. A candidate freeze proves artifact integrity, not human validity.

## Reproduction

Legacy local baseline:

```bash
python -m agrofield_agent.evaluate fixtures/eval_cases.jsonl
```

Blind-benchmark candidate:

```bash
python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl
```

Add `--require-validated` only with `--case-annotations`, `--output-reviews`, `--adjudications`, `--interviews`, `--human-freeze-manifest`, and `--freeze-root`. It exits 2 until every structural, human, privacy, freeze, agreement, and metric gate passes.
