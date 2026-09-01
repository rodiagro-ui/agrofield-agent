# Official rules freeze — 2026-09-01

Evidence captured on 2026-09-01 in America/Argentina/Buenos_Aires. Official rules can change; re-check before any publication or submission.

## Frozen facts

| Item | Verified fact | Source |
|---|---|---|
| Submission window | 2026-08-26 09:00 PDT through 2026-10-30 10:00 PDT. Argentina equivalent at deadline: **2026-10-30 14:00 ART**. | [Official rules](https://nebiusglobalaihackathon.devpost.com/rules) |
| Eligibility | Adults, teams, and organizations are eligible except listed restricted jurisdictions. Argentina is not excluded. | [Official rules](https://nebiusglobalaihackathon.devpost.com/rules) |
| Runtime requirement | The project must make a runtime call to Token Factory or run/deploy on Nebius AI Cloud compute, and must use at least one NVIDIA open-source model. | [Official rules](https://nebiusglobalaihackathon.devpost.com/rules) |
| Suggested track | Best Apps and Agents: a coherent application or agent people would actually use, powered by Nemotron through Token Factory. | [Hackathon overview](https://nebiusglobalaihackathon.devpost.com/) |
| Required deliverables | Working public URL, public open-source repository with visible license and reproducible README, description, feedback on Nebius/NVIDIA tools, and public YouTube demo no longer than three minutes. | [Official rules](https://nebiusglobalaihackathon.devpost.com/rules) |
| Existing work | A project started before 2026-08-26 needs a written explanation of significant updates during the submission period. | [Official rules](https://nebiusglobalaihackathon.devpost.com/rules) |
| Testing availability | Judges must receive free and unrestricted access through the judging period; private demos may provide credentials. Judges may rely only on the text, images, and video. | [Official rules](https://nebiusglobalaihackathon.devpost.com/rules) |
| Submission language | English, or English translations of the demo, description, testing instructions, and other materials. | [Official rules](https://nebiusglobalaihackathon.devpost.com/rules) |
| General prizes | US$20,000; US$10,000; US$6,000. | [Hackathon overview](https://nebiusglobalaihackathon.devpost.com/) |
| Track / sponsor prizes | Each track winner receives a Jetson Orin Nano; Best Use of Tavily is US$3,000. | [Hackathon overview](https://nebiusglobalaihackathon.devpost.com/) |
| Judging criteria | Technological implementation, design, potential impact, and quality of idea. No weights were published on the overview as of the capture date. | [Hackathon overview](https://nebiusglobalaihackathon.devpost.com/) |
| Current gallery | The project gallery was not yet published as of 2026-09-01. | [Project gallery](https://nebiusglobalaihackathon.devpost.com/project-gallery) |

## Credits, billing, and Argentina

- The Builder Program registration form visibly includes **Argentina** as a selectable country. Registration remains subject to verification and sanctions screening.
- The public Builder Program landing page advertises US$25 Token Factory credit, US$25 Tavily credit, and a US$1 Academy certification offer.
- The June 2026 legal terms additionally describe an initial US$25 AI Cloud credit and a second allocation after approximately 30 days, up to US$50 AI Cloud + US$50 Token Factory + US$25 Tavily. Because the landing page and terms do not fully match, the project budget treats only credits actually issued in the account as available.
- Promotional credits expire 90 days after issuance and are for prototyping/experimentation, not production workloads.
- Token Factory onboarding documentation says billing setup requires a bank card and includes US$1 trial credit valid for 30 days. Automatic charging can occur when a threshold is reached or a balance is negative. **Do not enable paid use without explicit authorization.**
- AI Cloud individual onboarding charges US$25 to the card and adds it to the account balance. This is a real payment and is outside the current authorization.
- Token Factory documentation currently says no additional VAT is added for the “rest of world,” but Argentine card taxes, exchange-rate treatment, or local tax obligations were not verified and should not be assumed away.

Sources: [Builder Program](https://dev.nebius.com/builders), [Builder Program terms](https://nebius.com/builders-terms-and-conditions), [Token Factory billing](https://docs.tokenfactory.nebius.com/other-capabilities/billing-new), [AI Cloud signup and billing](https://docs.nebius.com/signup-billing/sign-up).

## Available services and model evidence

The public Token Factory catalog was inspected on 2026-09-01. It listed public availability for:

- `Nemotron-3-Nano-30B-A3B` — text-to-text, FP8, 262K context.
- `Nemotron-3-Super-120b-a12b` — text-to-text, FP4, 256K context.
- `Nemotron-3-Ultra-550b-a55b` — text-to-text, FP4, 1,024K context.
- `Nemotron-3.5-Lightning` — text-to-text, BF16, 1,024K context.
- `Nemotron-Nano-V2-12b` — vision, BF16, 128K context.

Exact per-token prices were not visible without logging in. The pricing page states that model cards show input and output USD per million tokens, so price must be frozen from the authenticated account before a live evaluation run.

The Token Factory documentation confirms an OpenAI-compatible API, function calling, JSON-schema tool definitions, and that application code—not the model—must execute proposed tools. This matches the intended trust boundary.

Sources: [Nemotron on Token Factory](https://nebius.com/services/token-factory/nemotron), [Function calling documentation](https://docs.tokenfactory.nebius.com/ai-models-inference/function-calling), [Pricing documentation](https://docs.tokenfactory.nebius.com/ai-models-inference/playground).

## Publication and spending gates

The following remain blocked until explicit user authorization:

1. Add a card, accept a charge, or enable automatic billing.
2. Use paid Nebius or Tavily credits beyond an expressly approved cap.
3. Publish the repository or make it public.
4. Deploy a public application or keep a paid endpoint warm.
5. Upload the video publicly.
6. Register or submit a Devpost entry.

Local development, mocked integration tests, documentation, evaluation fixtures, and submission drafts are allowed.
