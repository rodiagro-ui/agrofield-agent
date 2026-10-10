# Token Factory billing recheck — 2026-10-10

Read-only observation of the authenticated Token Factory UI, made through the
session's browser pane after the owner logged in. Nothing was changed, no key
was created and no request was sent. Identity, card and address details shown
on `Billing details` are deliberately not recorded here.

| Item | Observed on 2026-10-10 (UTC) |
|---|---|
| Trial credits | US$1.00, `29 days left` (header chip and user menu) |
| Account balance | US$0.00 |
| Transactions, Oct 2026 | Consumption US$0.00, Trial US$0.00, closing balance US$0.00 |
| Usage, 2026-09-10 to 2026-10-10 | `No usage` |
| Nvidia-Nemotron-3-Nano-30B-A3B | Input US$0.06/M, Output US$0.24/M (valid from 01 Jan 2026); batch US$0.03/M and US$0.12/M |
| Nvidia-Nemotron-3-Super-120B-A12B | Input US$0.30/M, Output US$0.90/M |
| Post-trial preference | User menu shows **`Paid usage after trial`** next to a `post-trial-usage-button`; the 2026-09-15 record showed `Usage stops after the trial` |
| Billing | `Active`; a bank card is on file |

The documentation (`other-capabilities/billing-new`) states the card is charged
automatically at the start of a month with a negative balance or when a billing
threshold is reached.

## Consequence for the handoff gates

Prices are unchanged, so the single-request ceiling remains US$0.00122880 and
the 20-note batch worst case remains US$0.02457600, both far below the trial
credit. However the `Usage stops after the trial` control is **not confirmed**:
the UI currently reads `Paid usage after trial`. Per the handoff, the single
authorized request is not sent until the owner either sets the preference back
to stop usage or explicitly accepts paid usage after the trial.
