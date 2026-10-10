# Public demo deployment plan (not executed)

Goal: one public URL that judges can use free of charge until 2026-12-15, with
every analysis making a runtime Nemotron call through Token Factory and the
spend bounded by the application ledger plus the account's trial stop.

## Environment for the container

```
AGROFIELD_PROVIDER=nebius-demo
AGROFIELD_NEBIUS_DEMO_CONFIRMATION=RUN_PUBLIC_NEMOTRON_DEMO
AGROFIELD_DB_PATH=/data/agrofield.sqlite3
AGROFIELD_DEMO_LEDGER_PATH=/data/nebius-demo-ledger.sqlite3
NEBIUS_API_KEY=<demo key created for the deployment, never the owner's main key>
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1
NEBIUS_MODEL=nvidia/nemotron-3-super-120b-a12b
NEBIUS_INPUT_PRICE_PER_MILLION=0.3
NEBIUS_OUTPUT_PRICE_PER_MILLION=0.9
NEBIUS_MAX_COST_USD=0.01
NEBIUS_MAX_COMPLETION_TOKENS=1024
NEBIUS_PROMPT_TOKEN_BUDGET=16384
NEBIUS_REASONING_EFFORT=none
AGROFIELD_DEMO_TOTAL_BUDGET_USD=5
AGROFIELD_DEMO_DAILY_REQUESTS=300
AGROFIELD_DEMO_REQUESTS_PER_MINUTE=6
AGROFIELD_VERIFIER_MODEL=nvidia/nemotron-3-super-120b-a12b
NEBIUS_VERIFIER_INPUT_PRICE_PER_MILLION=0.3
NEBIUS_VERIFIER_OUTPUT_PRICE_PER_MILLION=0.9
```

Prices are those read in the authenticated console on 2026-10-10; recheck on the
day. With Super, one analysis costs about US$0.0014 plus a verification of
similar size; the ledger reserves the worst case (US$0.0058 per call) and settles
at reported usage. A US$5 budget therefore covers well over a thousand analyses,
and the daily and per-minute caps stop a bot before the budget does. When the
budget is exhausted the page says so and only the labeled local extractor
answers, so the URL never goes dark.

## Choosing the host

| Option | Cost | Notes |
|---|---|---|
| Hugging Face Space (Docker) | free | Public URL, sleeps after inactivity and wakes on request; `/data` is ephemeral unless persistent storage is paid, so the ledger resets on restart (caps still apply per process; keep the total budget small) |
| **Render Free (chosen)** | US$0, no payment method needed | Verified in docs on 2026-10-10: without a payment method Render suspends instead of billing; 750 free instance hours per month (one always-on service uses ~720); spins down after 15 idle minutes and takes about a minute to wake, showing a loading page; ephemeral filesystem, so the SQLite demo data and the spend ledger reset on every restart (caps still apply per process; keep the total budget small). Deploys from a public GitHub repo through Render's GitHub login; `render.yaml` in the repo is the blueprint. |
| Railway / Fly | trial credit or card | Not needed |
| Nebius AI Cloud (Serverless Endpoints / DevPod) | requires the US$25 card charge | Encouraged by the rules but not required; outside the current authorization |

Any choice needs the owner's account; the container is the same. With Render Free the
only secret typed anywhere is `NEBIUS_API_KEY`, entered by the owner in the Render
dashboard; `render.yaml` marks it `sync: false`. Judges should be told that the first
request after idle takes about a minute.

## Steps (owner present)

1. Create a dedicated Token Factory API key for the demo; keep the trial stop.
2. Build or point the host at this repository's `Dockerfile`; set the variables above.
3. Open `/api/runtime`: it must show `nemotron_runtime: true`, the Super model and
   the verifier, with the remaining budget.
4. Run the incomplete and complete notes once; check the audit trail shows
   `observation_verified` events and that the header badge reads
   `Nemotron · Token Factory`.
5. Record the budget readings before and after; keep them for the submission.
6. Revoke the demo key after the judging period ends (2026-12-15).
