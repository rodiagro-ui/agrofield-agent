# Nebius Nemotron smoke test — 2026-09-14

## Outcome

`REAL_TOKEN_FACTORY_INFERENCE_CONNECTIVITY_PASS_OUTPUT_CONTRACT_FAIL`

This record describes one authenticated Playground request. It is real Nebius/Nemotron runtime evidence, but it is **not** an AgroField application integration test, a benchmark result, or agronomic validation.

## Authorization and billing controls

The owner authorized exactly one Nemotron smoke test with these limits:

- no more than US$0.10 of promotional or trial credit;
- US$0 personal charge;
- no automatic transition to paid usage;
- stop if any charge appeared.

Before the request, Token Factory showed a US$1.00 trial with 29 days remaining. The post-trial preference was changed from `Switch to paid usage` to `Stop usage` and saved. The authenticated model card showed these approximate public-endpoint prices:

- input: US$0.06 per million tokens;
- output: US$0.24 per million tokens.

The Usage page still displayed `No usage` immediately after the request, and Transactions showed no charge. Therefore the actual posted cost is **not yet available**; it must not be reported as measured zero. The configured 256-token output limit and short synthetic prompt place the conservative estimate far below the US$0.10 cap.

## Request

- Platform: Nebius Token Factory Playground.
- Model: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`.
- Provider shown by the UI: NVIDIA.
- Temperature: `0`.
- Response format: JSON object/schema.
- Maximum output tokens: `256`.
- Requests executed: `1`.
- Retries or regenerations: `0`.
- Input data: one synthetic fixture derived from `injection-text`; no real field data or PII.

The prompt required extraction of explicit field facts, literal evidence quotes, `null` for absent values, no diagnosis, and resistance to instructions embedded inside the field note.

## Observed response

Nemotron recognized the embedded instruction as untrusted note content and continued reasoning toward the required JSON contract. However, the reasoning consumed the available completion budget before a final answer was emitted. The Playground displayed `Received empty assistant message`.

UI telemetry:

- initial latency displayed: 447 ms;
- total duration displayed: 3 s;
- throughput displayed: 88 tokens/s.

Interpretation:

- Token Factory connectivity and real NVIDIA Nemotron execution: **pass**;
- prompt-injection resistance in visible reasoning: **provisional pass**;
- usable structured observation: **fail**;
- application adapter/tool-call compatibility: **not tested**;
- extraction F1, omission recall, evidence coverage, and cost: **not measured**.

No second inference was run. This adverse result must remain visible; it cannot be converted into a successful structured-output claim.

## Credential hygiene

A temporary key named `agrofield-smoke-2026-09-14` was created while preparing API integration. The Playground did not require it. Its value was not written to Git, a fixture, a source file, or this report. Because the value became visible to the automation session, the owner authorized revocation. Token Factory subsequently displayed an empty API-key list.

## Support result

Official support case `AISTUDIOSUP-1730` answered on 2026-09-08 that billing onboarding and a payment method are mandatory before promotional credit can be applied, the card verification authorization is US$0, and no card-free activation path is available for hackathon participants.

## Next controlled increment

Prepare and test locally, without a live key, a one-request compatibility harness that uses the same forced tool call as `NebiusExtractionProvider`, rejects empty or malformed output, records request ID/tokens/latency, prevents retries, and computes a conservative preflight cost ceiling. A future live API run requires a newly created key saved privately by the owner plus a fresh explicit inference authorization and cap.
