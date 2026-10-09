# Owner checklist for the next session at the PC

Everything below needs the owner's own logins. Nothing here is automated, and
none of it has been done yet. Estimated time at the keyboard: 15 minutes.

## 1. Billing, on the day (Token Factory)

Open <https://tokenfactory.nebius.com> in the browser pane of the Claude session
(or paste screenshots in the thread) and read:

- promotional credit remaining and its expiry date;
- Nemotron 3 Nano price, input and output, USD per million tokens;
- account balance and any charge;
- whether `Usage stops after the trial` is still active.

If credit is insufficient, a charge appears, or the stop is not confirmed: do not
call. Otherwise the per-request ceiling is recomputed with those prices.

## 2. The single authorized inference

```powershell
.\.venv\Scripts\python.exe -m agrofield_agent.handoff_runner --mode live `
  --input-price-per-million <today> --output-price-per-million <today> `
  --max-cost-usd 0.01 --confirm-live RUN_ONE_NEBIUS_REQUEST `
  --report-file docs\submission\evidence\nebius-live-handoff-<date>.json
```

Create a temporary API key in Token Factory, open the printed loopback URL in
the local browser, paste the key once, submit, then **revoke the key** and check
that the key list is empty. The report is sanitized: it never contains the key.

## 3. Only after a good result, decide separately

- a batch of the 20 synthetic development notes through `nebius_eval`
  (worst case about US$0.025 at the 2026-09 prices; recompute with today's);
- a demo budget for the public instance (`nebius-demo` mode); a suggested
  starting point is US$1 total, 200 requests per day, 6 per minute, which the
  ledger enforces before any network call;
- a hosting choice and spend ceiling for the public URL;
- creating the public GitHub repository (MIT license visible) and pushing;
- the YouTube upload and the Devpost submission, before 2026-10-30 10:00 PDT.
