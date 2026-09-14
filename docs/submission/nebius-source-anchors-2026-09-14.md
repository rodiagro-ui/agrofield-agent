# Nemotron evidence source anchors — 2026-09-14

## Observed problem

The last historical live `/api/analyze` attempt reached local evidence validation
and returned `non-literal evidence quote for: event_type`. Its raw response was not
retained, so a translated or paraphrased quote is a possible explanation, not an
observed root cause. It must not be described as an upstream connection failure.

## Local correction

The request now contains a JSON catalog of at most 32 source fragments, identified
as `S01`, `S02`, etc. These are exact slices of the input, in original order. Long
notes keep the remaining text in the final fragment; decimal points are preserved.

The closed tool schema asks for `evidence_sources` (IDs per observed field) and
`note_sources` (IDs for additional observations). Both are constrained to IDs in
this request. AgroField resolves IDs against the original text before constructing
the unchanged `ObservationDraft.evidence_quotes` and `notes` fields. Multiple IDs
produce the smallest original contiguous excerpt covering their source spans.

Unknown IDs, duplicate IDs, free-form quotes, absent-field citations, missing
citations and malformed types are rejected. The final literal check now requires
an exact substring, without case folding or whitespace normalization. `policy.py`,
the local extractor, model classes and frozen benchmark files are unchanged.

The API returns safe provider diagnostics on contract failure: HTTP status,
request ID, token counts when available, response shape, and latency. It never
returns the rejected generated text or credentials. No automatic retry occurs.

This uses the existing explicit function call and JSON Schema enum mechanism
described in [Nebius function calling](https://docs.tokenfactory.nebius.com/ai-models-inference/function-calling).
The source-anchor design is an application decision, not a vendor guarantee.

## Verification before a live request

- 85 local tests pass, including 31 mocked Nebius tests and 9 source-span tests.
- The synthetic translation/reference failures are generated test data, not a
  replay of the unsaved live response.
- Legacy local F1: 0.9551; candidate local F1: 0.9188. Neither is a Nemotron result.
- Candidate adverse failures: 53; `benchmark_validated: false`; zero human reviews.
- Freeze: 34/34 matching hashes. Policy matches the original MVP.
- Network-free preflight: 5,885 bytes, 16,384 prompt-token ceiling, 1,024 completion
  ceiling and US$0.00122880 at US$0.06/M input and US$0.24/M output.

## Remaining limitations

Selecting a real source proves where a quote comes from, not whether the selected
value is semantically supported. A model can still cite the wrong sentence,
misread negation, or extract the wrong number. Those errors still require measured
evaluation and human review. This change does not establish agronomic validity,
model superiority, or live compatibility. A separately authorized live outcome
must be recorded independently of this pre-run verification.
