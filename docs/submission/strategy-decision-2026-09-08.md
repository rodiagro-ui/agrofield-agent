# Submission strategy decision — 2026-09-08

## Decision

The project owner chose to continue toward a hackathon presentation without waiting for the complete 30-primary/10-double human-review protocol.

This is a scheduling decision, not a validation result. It does not change the frozen benchmark, lower any evaluator threshold, or authorize a claim that the project was independently validated.

## Consequences

- `benchmark_validated` remains `false`.
- Existing synthetic references remain provisional.
- The 17 strict validation gates and `--require-validated` behavior remain unchanged.
- The submission may use reproducible local metrics only when labeled as synthetic deterministic baselines.
- The founder's written field-work account may guide product and demo design, but must be disclosed as non-independent first-party input.
- No human-performance, adoption, savings, or agronomic-accuracy claim may be inferred from that account.

## Compensating controls

1. Demonstrate the control boundary directly: evidence quotes, missing checks, deterministic blocking, named approval, and audit history.
2. Show measured Nemotron quality, latency, and cost only after a separately authorized live run.
3. Keep unsupported claims out of the video and Devpost copy.
4. Preserve adverse failures and the unvalidated benchmark status in the repository.
5. Treat additional independent review as a credibility improvement, not as a hidden prerequisite already satisfied.

## Still blocked

This decision does not authorize Nebius, Tavily, spending, repository publication, deployment, video upload, or Devpost submission.
