# Semantic smoke paused before inference — 2026-09-15

## Outcome and authority

`PAUSED_LOCAL_HANDOFF_FAILURE_NO_NEW_INFERENCE`.

The owner authorized one Nano request, zero retries, up to US$0.01 exclusively
from promotional credit, US$0 personal, and temporary-key creation/revocation.
They also required an immediate pause on an anomaly. The new inference allowance
was **not consumed**: the browser-to-local handoff was rejected before the
application was invoked. The session is paused pending explicit owner resumption,
not permission to create keys or retry automatically. The four September 14
inference authorizations remain consumed. Lifetime inference count remains four.

No new Nemotron observation, latency, tokens or quality score exists. This is a
local preparation failure, **not a Nebius endpoint or model failure**.

## Checks completed before creating a key

- Reviewed application revision `4d49a68` and required project documents; clean
  main branch before changes, 124 tests passing, one existing deprecation warning.
- Local 12-case F1 0.9551; omissions 1; unsupported 0; safety 1; nDCG 1.
- Local 30-case F1 0.9188; omissions 0.9714; unsupported 0.005; safety 1;
  nDCG 0.9877; benchmark_validated false. No human benchmark reviews.
- Frozen candidate 34/34 and semantic development package 8/8 valid.
- Semantic preflight: 20 synthetic development references, model quality null.
- Saved historical live-response audit reproduced its five field errors.
- `policy.py` remains identical to MVP `32855c4`; neither extractor, model
  contract, frozen references nor evaluator was changed during this session.
- Current authenticated account UI: US$1.00 trial display, 28 days remaining,
  `Usage stops after the trial`; balance US$0.00. Transactions displayed rounded
  consumption/trial US$0.00. These are dated UI observations, not a final invoice.
- [Account prices](https://tokenfactory.nebius.com/organization/prices): Nano
  input US$0.06/M and output US$0.24/M, ordinary inference, not batch.
- Exact model: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`; fixed synthetic note
  `fixtures/nebius_smoke_note.txt`; Tavily disabled.
- Serialized payload 9,776 bytes; prompt proxy ceiling 16,384, completion 1,024;
  cost estimate ceiling US$0.00122880. This proxy is a conservative estimate,
  not a provider-enforced dollar cap. Trial stop and one-request controls remain
  necessary. Payload SHA-256 (sorted compact UTF-8 JSON):
  `e77d52e90b705aef5953971b45d207ed7e5255ccc04a2c49eff73bf3b9a20a88`.

The console also announced a future September 21 storage migration and temporary
CPL/operations read-only period. No current billing failure was shown. This
notice was not tested for inference impact and is not the cause of this pause.

## Two local findings, kept separate

1. The disposable runner's mocked self-test passed the single-request contract
   but Windows initially could not delete a temporary SQLite file. Collecting
   released SQLite objects before temporary-directory cleanup resolved that
   helper issue; a repeated offline self-test exited 0. The leftover synthetic
   file/directory was removed. This did not change production Repository code.
2. After creating one temporary key privately, the local form returned `Blocked`
   (HTTP 403 in the helper) before reading its body or invoking AgroField.
   No response record or application database was created. The guard was not
   bypassed, and the form was not resubmitted with the key.

The key was revoked immediately after the failed handoff; the authenticated UI
showed `The API key list is empty`. The runner was terminated, its empty temporary
directory removed, private key/state variables and clipboard cleared, and both
disposable helper files removed. No key or account identity was written to Git.
The final transactions view again showed rounded consumption/trial US$0.00;
no personal charge was visible. This display is not a final billing invoice.

## Reproduced cause and local correction

A separate diagnostic with only `synthetic-only` as form data, **no credentials,
no application imports and no API client**, found:

| Check | `no-referrer` response policy | `same-origin` response policy |
|---|---|---|
| Path, Host, content type | Correct | Correct |
| Origin header present | Yes | Yes |
| Origin header value null | Yes | No |
| Origin exactly matches local server | No | Yes |
| Request body read / external inference | No / no | No / no |

The helper itself set `Referrer-Policy: no-referrer`. For non-CORS form POSTs,
the [Fetch Standard's Origin algorithm](https://fetch.spec.whatwg.org/#append-a-request-origin-header)
sets the serialized origin to null under that policy. With `same-origin`, it
preserves matching origins but still suppresses cross-origin disclosure. This
matches the observed before/after experiment; it is not a claim that the browser
or Nebius was faulty.

The retained diagnostic defaults to `same-origin`. Its guard still rejects
missing/null/foreign origins, a different port, an unexpected Host/content type,
and a wrong path. It never reads any submitted body, even when headers match.
It is **not** a credential-transfer or inference runner. A future live runner
must use the same safe header policy and pass a full browser-plus-mock rehearsal
before a real key is created. Do not fix this by accepting `Origin: null`.

## Reproduce without credentials or paid services

From the repository, using the local virtual environment:

```powershell
python -m pytest --override-ini addopts='' -q
python -m agrofield_agent.handoff_preflight
# Open the printed loopback URL, leave the dummy text unchanged, submit once.
# Expect guard_would_accept=true; API execution remains unavailable.
python -m agrofield_agent.handoff_preflight --referrer-policy no-referrer
# A new local URL reproduces the rejection; never enter a key.
```

The server binds only 127.0.0.1:18092, closes after one diagnostic POST or a
three-minute idle deadline, logs no raw header values/body and writes no files.
The retained default tool was also verified through the actual in-app browser.
Its source and nine regression tests are committed as `27ca97b`.
The suite now has **133 passing tests**, including nine new diagnostic tests.
Both freezes remain 34/34 and 8/8. Existing Starlette deprecation warning remains.

## Next step

Honor the requested pause. Resume the previously authorized single inference
only after the owner explicitly resumes, a complete mock browser handoff passes,
and prices/credit/Stop usage are rechecked. Do not ask for or infer a wider budget.
Compare all 12 fields against the unchanged synthetic development reference;
retain adverse results. One good response still would not validate the benchmark
or establish model superiority. No Tavily, publication or submission is authorized.
