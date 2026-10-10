# Capped batch under profile v3: Nano and Super — 2026-10-10

One paste of the owner's temporary key into the single-use batch form ran the 20
AI-authored synthetic development notes twice through the guarded contract
(`source-anchors-es-v3-semantic-candidate`): first `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`,
then `nvidia/nemotron-3-super-120b-a12b`. One request per note, zero retries,
Tavily off, shared cap US$0.20. Sanitized report:
`evidence/nebius-batch-v3-nano-super-2026-10-10.json`. Total estimated cost
US$0.03081024; 40 requests.

| | Nano, v2 (earlier today) | Nano, v3 | Super, v3 | Local extractor |
|---|---:|---:|---:|---:|
| Accepted / 20 | 8 | 10 | **18** | 20 |
| Micro-F1 (rejected notes count their expected facts as lost) | 0.52 | 0.6545 | **0.9343** | 0.8219 |
| Precision / recall | 0.867 / 0.371 | 0.900 / 0.514 | **0.955 / 0.914** | 0.790 / 0.857 |
| Unsupported assertion rate | 0.033 | 0.075 | **0.030** | 0.132 |
| Notes fully right / 20 | 1 | 6 | **15** | 7 |
| Latency p50 / p95 | 2.9 / 4.0 s | 3.6 / 4.7 s | **2.3 / 2.7 s** | <2 ms |
| Tokens in / out | 25,767 / 2,365 | 32,702 / 2,819 | 60,367 / 5,435 | 0 |
| Cost per accepted note | US$0.00066 | US$0.00053 | US$0.00142 | US$0 |

Every rejection this time was `missing evidence quote for` a field: the model
asserted a value with an empty `evidence_sources` list, and the contract refuses
a fact without a literal source. That is the intended safety behavior; a future
version could drop such a value to null and flag it instead of rejecting the
whole response, which would be strictly more conservative.

Super's five remaining errors: one unsupported `access_safe` on a forecast note,
one unsupported `standing_water_pct` plus a missing `event_type` on a partial-area
note, and one swapped time with a missing area on a reordered note. Nano still
returns empty observations on negated or unit-less notes and copies percentages
across denominators.

## Decision and limits

Nemotron 3 Super is the extraction model for the demo; Nano is kept as the cost
reference. All references are AI-authored synthetic development notes: this is a
development diagnostic that now compares three extractors on the same 20 notes,
not a validated benchmark and not agronomist evidence. The second-pass verifier
(`support-judge-es-v1-candidate`) was not part of this batch.
