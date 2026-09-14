# Guarded Nebius API smoke — 2026-09-14

> Resultado: `REAL_AGROFIELD_HARNESS_REQUEST_CONNECTIVITY_PASS_TOOL_CONTRACT_FAIL`

This record describes exactly one authenticated request sent by AgroField's guarded
compatibility harness to the shared Nebius Token Factory API. It is real
Nebius/Nemotron runtime evidence. It is **not** a successful structured extraction,
a FastAPI `/api/analyze` end-to-end run, a benchmark result, or agronomic validation.

## Authorization and hard limits

The owner explicitly authorized:

- model: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`;
- maximum: one API request and zero retries;
- maximum promotional-credit exposure: US$0.01;
- personal charge: US$0;
- a temporary key created only for this test and revoked afterward;
- stop if current prices, promotional credit, or the `Stop usage` fallback could not
  be verified.

The authorization was consumed by this request. It does not permit another Nebius
or Tavily call.

## Verified preconditions

Immediately before the request, the authenticated Token Factory interface showed:

- trial balance: US$1.00 with 29 days remaining;
- post-trial behavior: usage stops after the trial;
- Nano input price: US$0.06 per million tokens;
- Nano output price: US$0.24 per million tokens.

The local network-free preflight then reported:

| Guard | Value |
|---|---:|
| Serialized request | 2,908 bytes |
| Prompt-token ceiling | 16,384 |
| Completion-token ceiling | 1,024 |
| Conservative cost ceiling | US$0.00122880 |
| Authorized cap | US$0.01 |

The ceiling was below the authorization by more than 8x.

## Exact execution boundary

The request was sent by:

```text
python -m agrofield_agent.nebius_smoke
```

The harness used the repository's guarded provider contract and sent one `POST` to
`https://api.tokenfactory.nebius.com/v1/chat/completions` with:

- `tool_choice` fixed to `record_field_observation`;
- `temperature: 0`;
- `reasoning_effort: low`;
- `max_completion_tokens: 1024`;
- `n: 1`, `stream: false`, and `store: false`;
- the synthetic note in `fixtures/nebius_smoke_note.txt`.

No retry was configured or attempted. The temporary secret was passed from the
clipboard to one child-process environment only. It was not written to `.env`, a
source file, a fixture, documentation, Git, or browser-side application code.

## Result

Token Factory returned a successful HTTP/JSON response, proving authenticated API
connectivity from the AgroField repository code. The strict parser then rejected the
response with:

```text
empty or invalid assistant message: exactly one tool call is required
```

Therefore:

- authenticated Nebius API connectivity: **pass**;
- NVIDIA Nemotron model invocation: **pass**;
- exactly-one-request / zero-retry control: **pass**;
- forced-tool output contract: **fail**;
- literal-evidence validation: **not reached**;
- end-to-end FastAPI route: **not tested live**;
- benchmark quality, latency, token usage, and measured cost: **not available**.

Because contract validation stops before telemetry acceptance, the result does not
contain a trusted request ID, prompt-token count, completion-token count, latency, or
measured cost. The authenticated usage page immediately afterward still displayed
`No usage`, while the trial badge remained US$1.00. That view may be rounded or
delayed and must **not** be cited as proof of zero cost.

## Credential cleanup

After the single request:

1. the process environment containing the key ended;
2. the clipboard was cleared;
3. the owner gave action-time confirmation to revoke the temporary key;
4. Token Factory displayed `The API key list is empty`.

The key briefly became visible to the authorized automation session during creation,
so revocation was mandatory. Its value is intentionally absent from this repository.

## Claim boundary and next step

This run upgrades the evidence from Playground-only connectivity to a real request
originating in AgroField's guarded repository code. It does not prove that Nemotron
can satisfy the current tool contract, and it does not replace a live `/api/analyze`
demo or a frozen-suite evaluation.

The next highest-ROI work is network-free: inspect the official function-calling
contract and harden the parser/request compatibility using captured synthetic mocks.
Any second live request requires a new explicit authorization, a new cap, fresh price
and billing checks, and a new temporary key.
