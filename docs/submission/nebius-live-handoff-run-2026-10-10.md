# Live browser handoff run — 2026-10-10

## Outcome

`LIVE_ROUTE_CONTRACT_PASS_SINGLE_NOTE`. The single request authorized on
2026-09-15 and resumed on 2026-09-18 was consumed today through the complete
path: the owner pasted a temporary key into the local single-use form in his own
browser, the loopback server accepted exactly one POST, `/api/analyze` ran with
the guarded provider and the real Nebius transport, and the response passed the
contract. Lifetime real inference count is now five. Billing was rechecked the
same day (`nebius-billing-recheck-2026-10-10.md`): unchanged Nano prices, US$1.00
trial credit, US$0.00 balance, post-trial preference set to stop usage.

## Measured

| Item | Value |
|---|---|
| Model | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`, profile `source-anchors-es-v2-semantic-candidate` |
| Route | `/api/analyze`, FastAPI in process, real HTTPS to Token Factory, Tavily off |
| HTTP status | 200 |
| Latency | 2,374.8 ms |
| Tokens | 3,259 input / 290 output |
| Estimated cost | US$0.00026514 from reported usage at US$0.06/M and US$0.24/M (ceiling US$0.00122880) |
| Request ID | `3214519921009416fdb5e924c416d1f6` |
| Retries | 0 |
| Policy | `blocked`, missing `stand_count_per_m`; one task pending, none decided |

## Quality against the fixed synthetic reference

`fixtures/nebius_smoke_reference.json`, same note as the 2026-09-14 run:
**12/12 fields** (8 observed correct, 4 correctly absent), no missing, wrong or
unsupported values; every nonempty quote literal; `general_condition` reported
as uncertain, which is consistent with the note. The 2026-09-14 run under the
previous profile scored 4/8 observed with one unsupported value.

This is one developer-authored synthetic note. It is not a benchmark, not
agronomist validation, and does not by itself demonstrate that the v2 profile is
better in general; it is the first live evidence consistent with that candidate.

## Controls

The sanitized report `evidence/nebius-live-handoff-2026-10-10.json` records that
the submitted value was not found in the environment, temporary files or the
report, and that the server and temporary SQLite were removed. The temporary key
was additionally pasted by the owner into the project chat during the session
and must therefore be revoked regardless of the run; the owner was asked to do so.

## Reproduce the comparison offline

```powershell
.\.venv\Scripts\python.exe -c "import json;from agrofield_agent.smoke_audit import compare_fields as c;r=json.load(open('docs/submission/evidence/nebius-live-handoff-2026-10-10.json'));e=json.load(open('fixtures/nebius_smoke_reference.json'))['expected'];print(c(r['analysis']['observation'],e))"
```
