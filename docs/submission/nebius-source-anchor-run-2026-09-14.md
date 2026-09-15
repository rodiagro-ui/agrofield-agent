# First accepted Nemotron extraction: contract pass, quality failure

> Run: 2026-09-14 23:03 UTC. Report updated 2026-09-15. One synthetic
> development note, not an agronomy benchmark or independent validation.

## Authorization and containment

This separately authorized run allowed one request, zero retries, a maximum of
US$0.01 from promotional credit only, and US$0 personal charge. The authorization
is consumed. It does not authorize another inference, Tavily, or publication.

Before the request, the authenticated Token Factory UI showed US$1 trial credit,
29 days remaining, `Usage stops after the trial`, and an account balance of zero.
The Nano public-endpoint price was US$0.06/M input and US$0.24/M output. Those
observations are historical, not reusable billing guarantees.

A temporary API key was created privately, used only for this request, revoked,
and the key list verified empty. No key was written to Git or the report. The
temporary local credential handoff process was stopped, its helper removed, and
the session variables and clipboard cleared. Tavily was disabled. A preliminary
local credential-transfer check stopped before sending a request; it is not an
additional inference. A UI timeout after submission did not trigger a retry.

## What ran

- Application commit: `1c432ed` — source IDs resolved into original note excerpts.
- Model: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` on Nebius Token Factory.
- Route: `POST /api/analyze` through FastAPI **TestClient in-process**, with an
  actual outbound Nebius HTTPS request. This was not a public deployment or a
  browser-to-public-server end-to-end test.
- Storage: isolated temporary SQLite database; no real field or personal data.
- Input: `fixtures/nebius_smoke_note.txt`, the existing synthetic development note.
- One analyze request, zero automatic retries.

The sanitized record is
[`evidence/nebius-source-anchor-smoke-2026-09-14.json`](evidence/nebius-source-anchor-smoke-2026-09-14.json).
It retains the accepted observation, usage, request ID, original-note hash and
policy summary. It is a sanitized application record, not a retained raw HTTP
response or a billing invoice.

## Integration result

| Measure | Observed result |
|---|---|
| Local route status | HTTP 200; `live_route_contract_pass` |
| Latency around extraction | 7,591.67 ms; a single measurement, not p95 |
| Reported input/output tokens | 2,288 / 311 |
| Estimated request ceiling before call | US$0.00122880 |
| Usage-derived cost estimate | US$0.00021192 |
| Literal quotes | All nonempty quotes were exact original-note excerpts |
| Deterministic policy | `blocked` |
| Proposed tasks | 1, still pending; none approved or executed |
| Audit event types | `analysis_created`, `demo_seeded` |

Cost estimate: `(2288 × 0.06 + 311 × 0.24) / 1,000,000`. The immediate post-run
transactions UI still rounded consumption and trial usage to zero; no personal
charge was visible. That display is not proof of zero usage cost or final billing.

## Quality result: not acceptable yet

The reference is a **developer-authored synthetic reference**, not a human
agronomist label. Its expected values were already in the mocked valid-response
test before this live call. The field-by-field audit is new, uses this exposed
development case, and must not be described as blind or held-out evaluation.

| Field | Developer reference | Saved Nemotron output | Diagnostic |
|---|---|---|---|
| Event type | `flooding` | `mixed` | Wrong value |
| Event age | 18 hours | `null` | Explicit information omitted |
| Standing water | 35% | `null` | Explicit information omitted |
| Water duration | 14 hours | `null` | Explicit information omitted |
| General condition | `unknown` | `mixed` | Unsupported assertion |

Out of eight expected observed fields, local deterministic extraction got eight
right and the saved Nemotron output got four right. Of four fields that should
remain unknown, Nemotron correctly left three unknown but asserted a general
condition. The audit examines all 12 observation fields, unlike the aggregate
benchmark's separate metric definitions; no F1 or statistical superiority claim
is derived from this single note.

The policy blocked because event age, standing-water percentage, water duration,
and stand count were missing in the model output. The first three omissions are
**extraction failures**; only stand count was actually absent from the note. A
blocked decision is safe in this case but does not make the extraction correct.

Literal provenance is not semantic support. A real sentence can be cited for the
wrong value. No safety, agronomic correctness or product-readiness guarantee can
be inferred from passing the schema and literal-quote contract.

## Reproduce without network or credits

From the repository root with the environment activated:

```powershell
python -m pytest -q
python -m agrofield_agent.smoke_audit
python -m agrofield_agent.evaluate fixtures/eval_cases.jsonl
python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl
python -m agrofield_agent.freeze benchmark/agronomy_blind_v1/freeze/manifest.json --root .
```

The audit reads the saved response and recomputes local extraction; it never calls
Nebius. The note hash prevents accidental comparisons against a different input.
Local suite after adding the audit: 88 tests passing, including 31 mocked guarded
Nebius tests, nine source-span tests and three saved-response audit tests.
The local 12/30-case baselines are unchanged. Freeze remains 34/34 valid;
`benchmark_validated: false`; no human benchmark reviews; `policy.py` unchanged.

## Next bounded increment

Clarify field meanings and extraction instructions locally, using new **development**
cases for event/water distinctions, unknown conditions, negation and time/quantity
binding. Preserve this adverse response and freeze; do not tune on the holdout or
replace missing Nemotron values silently with local values. Mock tests can verify
the request and safety contract but cannot demonstrate better model quality.
Any claim of improvement requires a separately authorized, capped live comparison
with the old result retained. Public demo and full-suite evaluation remain pending.
