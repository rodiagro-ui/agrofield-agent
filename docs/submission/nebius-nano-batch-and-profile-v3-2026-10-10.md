# Capped Nano batch and profile v3 — 2026-10-10

## The batch

Right after the single accepted request of the same morning (12/12 fields on the
smoke note), the owner pasted the same temporary key once into the single-use
batch form and the 20 AI-authored synthetic development notes ran through the
guarded contract on `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`, profile
`source-anchors-es-v2-semantic-candidate`, one request per note, zero retries,
Tavily off, cap US$0.05. Sanitized report: `evidence/nebius-batch-nano-2026-10-10.json`.

| Item | Value |
|---|---|
| Requests sent / accepted / contract-rejected | 20 / 8 / 12 |
| Latency p50 / p95 / mean | 2,884.9 / 3,961.2 / 3,010.9 ms |
| Tokens | 25,767 input / 2,365 output |
| Estimated cost | US$0.00527040 total, US$0.00065880 per accepted note |
| Nemotron (accepted responses; rejected ones count their expected facts as lost) | precision 0.8667, recall 0.3714, micro-F1 **0.52**, unsupported rate 0.0333, 1/8 notes fully right |
| Local extractor, same 20 notes | precision 0.7895, recall 0.8571, micro-F1 **0.8219**, unsupported rate 0.1316, 7/20 fully right |

Every rejected response contained exactly one well-formed tool call that stopped
normally (about 300 completion tokens); the rejection came from our own client
contract, not from the transport or the token budget. The exact rule was not
recorded by that version of the evaluator. Among the accepted responses, three
notes came back entirely empty with all twelve fields listed as uncertain, and
two notes reported `crop_stage` "V3" where the note said "V4", which matches
the example value in our own schema description.

These are synthetic, AI-authored development references, not agronomist labels,
and the batch is a development diagnostic, not a benchmark. It does establish
that the single-note result was the easy case.

## Profile v3, versioned

The changes are in `fixtures/development/semantic_v3/README.md`: no example value
in the crop-stage description; a sentence that explains a null field goes to
`note_sources`; `uncertainties` never lists established or merely absent
fields; the contract keeps a source attached to a null field as a literal note
instead of rejecting the response, fills an omitted empty list with `[]`, and
collapses repeated uncertainty entries. Missing value fields, extra keys,
unknown source IDs and non-literal notes still fail closed, and nothing adds a
value the model did not assert. The evaluator now records the fixed-string
reason of every rejection. The references were not edited. New freeze
`fixtures/development/semantic_v3/manifest.json` is 8/8; the v2 manifest is
historical and reports three mismatches by design. The human-benchmark freeze
remains 34/34 and `policy.py` is unchanged.

No live result of v3 exists yet; the next capped batch will show whether the
rejection rate was contract-side and what Nano and Super actually score.
