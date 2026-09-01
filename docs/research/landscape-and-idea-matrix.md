# Landscape, workflow, and idea matrix

Research freeze: 2026-09-01.

## What recent winners signal

The August 2026 Nebius Serverless AI Builders Challenge rewarded projects that paired a narrow problem with measured evidence and reproducibility:

- MediSimplifier quantified factual preservation, ran ablations, reported a real US$320 bill, and found low agreement between LLM judges.
- A model-evaluation dashboard compared quality, latency, and cost on user data rather than generic leaderboards.
- Balagan injected controlled failures, measured accuracy/token trade-offs, and reported a US$3.64 bill.
- The Agents special award went to a workflow turning financial documents into controlled records.

The repeatable pattern is: constrained workflow + visible control boundary + reproducible measurement + honest cost. Source: [Nebius winners announcement](https://nebius.com/blog/posts/serverless-ai-builders-challenge-winners).

## Competitive pressure

The broad “AI agronomist with voice, weather, history, and tasks” space is already crowded:

| Comparable | Existing overlap | Implication |
|---|---|---|
| Field Agent (Devpost, 2026) | Voice/SMS, weather, NDVI, soil, costed action plan | A one-message autonomous recommendation is not novel and is risky. |
| AgriScout AI (Devpost, 2026) | Multi-sensor field scouting, belief updates, work order, human gate | Avoid competing on drones/robots and generic diagnosis. |
| agrOS | WhatsApp voice/text, triage, alerts, tasks, auditable farm memory | Voice-to-records is a product feature, not a differentiator. |
| Solvata | Voice-first scouting, prioritized tasks, searchable memory | Same conclusion. |
| Tellia | Phone/WhatsApp notes into reports, tasks, logs, block association | Same conclusion. |
| OneSoil Scouting | Field history, weather, notes, photos, satellite layers, collaboration | A dashboard + notes is insufficient. |
| DeepLeaf | Photo/voice to grounded action using live field data | Avoid claiming a generic “digital agronomist.” |

Sources: [Field Agent](https://devpost.com/software/field-agent), [AgriScout AI](https://devpost.com/software/agri-scout-ai), [agrOS](https://www.tryagros.ai/), [Solvata](https://solvata.farm/), [Tellia](https://tellia.com/), [OneSoil](https://play.google.com/store/apps/details?id=io.onesoil.scouting), [DeepLeaf](https://deepleaf.io/solutions/agronomist).

## Conceptual field-scouting workflow

This is a hypothesis to validate with 3–5 Argentine advisers; it is not presented as completed user research.

1. **Before leaving:** identify the weather event, affected farms/lots, crop stage, access constraints, and prior weak spots; choose an efficient priority order.
2. **At the lot:** confirm lot identity, crop/stage, timestamp, safety, and whether the observed area is representative.
3. **Traverse:** inspect a W/Z/diamond path and deliberate trouble spots; do not infer field condition from the entrance alone.
4. **Measure:** record multiple sample points, stand/regrowth, affected area, water duration/depth, lodging/stem injury, weed/disease/pest signals, and photos or samples where uncertainty remains.
5. **Close the visit:** convert free speech into structured evidence, surface ambiguous or missing critical fields, and ask only the minimum follow-up questions.
6. **Human decision:** adviser approves, edits, defers, or rejects proposed actions. Direct treatment remains outside the autonomous boundary.
7. **Follow-through:** create owner/due-date tasks, schedule a re-scout window, and retain the evidence and decision history for the lot.

Evidence behind the workflow: Iowa State recommends a planned W/Z/diamond route, multiple stops, and 50–100 plants for general scouting; it stresses records and field history. INTA Rafaela reports recording coverage, uniformity, phenology, pests, diseases, weeds, weather events, sowing/harvest dates, rainfall, and water table. Recent storm guidance warns against immediate hail decisions and calls for delayed regrowth assessment. Sources: [Crop Scouting Basics](https://crops.extension.iastate.edu/encyclopedia/crop-scouting-basics), [INTA Rafaela monitoring report](https://repositorio.inta.gob.ar/bitstream/handle/20.500.12123/20121/INTA_CRSantaFe_EEARafaela_Informacion_tecnica_Produccion_Vegetal_2023.pdf), [2026 storm damage guidance](https://crops.extension.iastate.edu/post/storm-damage-june-2026).

## Idea matrix

Scores are 1 (weak) to 5 (strong). “Crowding” is reversed: 5 means low competitive crowding. Weights: impact 25%, demonstrability 20%, differentiation 20%, evaluation 15%, feasible delivery 15%, Tavily fit 5%.

| Idea | Impact | Demo | Differentiation | Evaluation | Feasibility | Tavily fit | Weighted |
|---|---:|---:|---:|---:|---:|---:|---:|
| Generic voice agronomist + tasks | 4 | 5 | 1 | 3 | 4 | 3 | 3.35 |
| Photo-first disease diagnosis | 4 | 5 | 1 | 2 | 2 | 2 | 2.85 |
| Pest-alert monitor + scouting route | 4 | 4 | 3 | 3 | 4 | 5 | 3.70 |
| Spray-window / label compliance copilot | 5 | 4 | 4 | 4 | 2 | 5 | 4.00 |
| Hail insurance evidence pack | 3 | 4 | 4 | 4 | 4 | 2 | 3.70 |
| **Post-event soybean scouting completeness gate** | **5** | **5** | **5** | **5** | **4** | **4** | **4.75** |

## Recommendation

Build **AgroField Agent: post-event soybean scouting completeness gate**.

The agent does not answer “what should I spray?” It answers four operational questions:

1. Which lots should we inspect first and why?
2. What evidence must the scout collect in each lot?
3. What did the voice note actually establish, and what remains unknown?
4. Which follow-up tasks are ready for an adviser to approve?

The differentiator is **proof of sufficient observation**, not eloquent agronomic advice. A red “decision blocked” state caused by a missing sample count or event duration is a product feature and an evaluation target.

## Runtime Tavily decision

Use Tavily only for fresh official alerts that may change scouting priority or add a targeted observation. Search with `include_domains`, Argentina boost, basic depth, and a small result cap. Examples: recent INTA pest alarm, SMN warning, or official extension storm bulletin. Each result must retain source URL and published date; stale or low-relevance results are discarded. External alerts may raise inspection priority but may not establish what is present in a specific lot or authorize treatment.

Tavily supports domain allowlists, date filters, Argentina country boost, and basic searches at one API credit. The current free plan advertises 1,000 credits/month. Sources: [Search API](https://docs.tavily.com/documentation/api-reference/endpoint/search), [credits](https://docs.tavily.com/documentation/api-credits).

## Questions for real interviews

1. Describe the last post-storm morning: who decided which lots to visit first?
2. What is usually missing from WhatsApp voice notes when you need to decide?
3. Which observations can a scout make reliably, and which require the adviser?
4. What makes you revisit after 24 hours versus 5–7 days?
5. What is the cost of an unnecessary trip, a missed lot, or a premature intervention?
6. What must be captured for insurance, contractor coordination, or client reporting?
7. Which data already exists per lot, and how often is it wrong or stale?
8. Would a “decision blocked—two checks missing” state help or irritate? Why?

The hypothesis should be revised if advisers do not recognize incomplete evidence and cross-lot prioritization as a frequent, costly problem.
