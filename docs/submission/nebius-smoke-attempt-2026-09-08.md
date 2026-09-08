# Nebius smoke-test attempt — 2026-09-08

## Outcome

`BLOCKED_BEFORE_INFERENCE_BY_MANDATORY_CARD_ONBOARDING`

The owner authorized one Nemotron smoke test with these hard limits:

- maximum promotional-credit consumption: US$0.10;
- maximum personal charge: US$0;
- automatic charging must remain disabled;
- stop if the account requires a card or presents any possible charge.

## Observed state

After authentication, the Token Factory onboarding page required billing identity fields and an **Add card** step before billing details could be saved. The page described a temporary US$0 card authorization. No card-free continuation was visible in the authenticated onboarding state.

The card step was not opened or completed because it was outside the authorization.

## Verifiable result

- Card data entered: no.
- Billing setup saved: no.
- Automatic charging enabled: no.
- API key created: no.
- Nemotron inference requests: 0.
- Tavily requests: 0.
- Promotional credits consumed: US$0.
- Personal charge: US$0.
- Nemotron metrics produced: none.

This attempt does not satisfy the hackathon runtime requirement and must not be described as a Nemotron run.

## Safe next options

1. Ask Nebius or the hackathon organizers for a card-free Builder Program/hackathon access path.
2. Use an already-issued card-free project or API key only if its balance and charging controls can be verified without exposing the key.
3. Request new authorization only if the owner later chooses a materially different billing approach.

Do not retry the paid-service path under the current authorization unless a card-free route becomes available.
