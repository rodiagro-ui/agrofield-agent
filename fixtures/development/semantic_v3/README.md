# Semantic development package v3

Same 20 AI-authored synthetic development cases as `semantic_v2` (byte-identical
`cases.jsonl`; no reference was edited after observing results). What changed is
the extraction profile, versioned as `source-anchors-es-v3-semantic-candidate`
after the capped 20-note Nemotron Nano batch of 2026-10-10 rejected 12/20
well-formed tool calls and copied the schema example "V3" into two notes:

- the crop-stage description no longer contains an example value;
- the instructions say that a sentence explaining a null field belongs in
  `note_sources`, and that `uncertainties` never lists established or merely
  absent fields;
- the client contract keeps a source attached to a null/unknown field as a
  literal note instead of rejecting the response, fills an omitted empty list
  with `[]`, and collapses repeated uncertainty entries. A missing value field,
  an extra key, an unknown source ID or a non-literal note still fail closed.

None of this adds or changes a value the model did not assert. The v2 manifest is
kept as a historical record and now reports three source files as mismatches
by design (`extraction_contract.py`, `nebius_smoke.py` and the default dataset
path in `semantic_preflight.py`). `preflight.json` here carries the v3 request fingerprints.
No live result of v3 exists until a new capped batch is recorded.
