# Semantic extraction v2 — development candidate

> AI-authored synthetic references, not human labels. All 20 cases are development
> material, not holdout, not an independent benchmark. No Nemotron call was made.

## Purpose and scope

This set targets the errors observed in the first accepted Nano response: event
age vs water duration, total affected area vs standing water, and event type vs
crop condition. Additional cases cover negation, conflicting statements, units,
other fields, forecasts, explicit zero and embedded instructions.

The references and rationales are deliberately visible to development. The old
12-case fixtures, 30-case frozen benchmark, its rubric/gates, and the real adverse
response remain unchanged. This is not a new human-benchmark version. No case is
copied verbatim from those sets or the historical smoke note.

## Candidate contract

Profile: source-anchors-es-v2-semantic-candidate.
Implementation: src/agrofield_agent/extraction_contract.py and nebius_smoke.py.
Runtime change commit: 6d7a5a8.

All 12 observation fields now have explicit Spanish meanings and distinctions.
The wire keys, source-ID resolution, policy.py, shared model, local extractor,
one-request ceiling and zero-retry rule are unchanged. Quantities must also be
nonnegative and finite in client-side validation; negative event ages/counts and
nonfinite values can no longer rely on missing constraints in the shared model.

These descriptions are instructions, NOT executable proof of semantic support.
Wrong supported-looking values may still pass. There is no repair call, second
LLM judge or silent local fallback. Ambiguous fields remain unknown with the
uncertainty and relevant source fragments retained.

## Reference convention

Each JSONL record includes all 12 expected fields, canonical supporting source
IDs, uncertainties, additional note sources, focus and rationale. Explicit unknowns
are distinct from zero/false. The reference source IDs demonstrate one suitable
citation; they are not the only possible correct citation.

Unit conversions use only explicit durations (minutes to hours); no inferred
clock, date, percentage of a subarea or plant density is introduced. For values
whose scope is ambiguous, the reference preserves unknown instead of calculating
a new agronomic fact. These conventions still need independent domain review.

The preflight checks structural representability, literal sources, request hashes
and the existing budget guard. It does not evaluate a model, assess agronomic
truth, judge task quality or score mock responses against their own labels.
nemotron_quality stays null and benchmark_validated stays false.

## Cases

| ID | Focus | Reference rationale |
|---|---|---|
| D01 | separate_times | El evento y la permanencia del agua tienen tiempos distintos; no inferir condición del cultivo. |
| D02 | missing_event_time | La duración del agua no es la edad de la tormenta. |
| D03 | missing_water_time | No completar duración o superficie a partir de la hora del evento. |
| D04 | different_percentages | Área afectada total y área con agua no son intercambiables. |
| D05 | negated_hazard | Granizo negado no convierte el evento en mixto; daño no medido no es cero. |
| D06 | unconfirmed_hazards | Nombrar peligros no evaluados no confirma que existan. |
| D07 | confirmed_mixed | Hay dos peligros positivos explícitos; condición general sigue desconocida. |
| D08 | condition_not_event | Buen estado del cultivo no prueba ausencia de un evento. |
| D09 | other_field | No transferir al lote actual el granizo, tiempo o superficie del vecino. |
| D10 | plants_vs_points | Cantidad de plantas no es cantidad de puntos; decimal y unidad deben preservarse. |
| D11 | damage_denominators | Defoliación no es tallo dañado ni área del lote; acame no confirma causa viento. |
| D12 | embedded_instruction | Las órdenes incrustadas no son hechos ni autorizan decisiones. |
| D13 | conflicting_time | Conservar la contradicción sin elegir una hora ni promediarla. |
| D14 | explicit_zero | Cero confirmado sí se conserva; no inventar duración ni estado general. |
| D15 | count_without_unit | Un conteo sin longitud no es plantas por metro; entrar no implica acceso seguro. |
| D16 | forecast_not_observed | Pronóstico, otro lote e ingreso no establecen evento, hora ni seguridad actuales. |
| D17 | explicit_unit_conversion | Conversión de minutos a horas es aritmética explícita, no una fecha inferida. |
| D18 | partial_area_denominator | El 20% no tiene denominador lote; no copiarlo ni calcular un porcentaje derivado. |
| D19 | negated_condition | Seguridad del acceso no establece condición del cultivo; no ignorar la negación. |
| D20 | reordered_same_source | Dos tiempos en el mismo fragmento: asociar cada uno con su variable, no con su orden. |

## Reproduce offline

From the repository root:

    python -m agrofield_agent.semantic_preflight
    python -m pytest tests/test_semantic_contract.py tests/test_nebius_smoke.py -q
    python -m agrofield_agent.freeze fixtures/development/semantic_v2/manifest.json --root .
    python -m agrofield_agent.smoke_audit

preflight.json is the deterministic output of the first command. It contains no
generated model response, human review, credential, contact or real field data.
It fingerprints each exact prospective request, not an executed request.

Using historical 2026-09-14 Nano prices purely for arithmetic:

- largest serialized request across these 20 cases: 9,999 bytes;
- existing prompt ceiling: 16,384 tokens, completion ceiling: 1,024;
- conservative per-request ceiling: US$0.00122880;
- existing smoke-note request: 9,776 bytes, previously 5,885 bytes.

The longer request may increase actual input tokens and latency. No current price,
availability, account credit, new expense or latency improvement is asserted.
This report does not authorize a single call or a 20-case batch.

## Integrity and future comparison

manifest.json freezes this candidate's references, instructions, contract
dependencies, offline checker and preflight report. Its validity demonstrates
file integrity only. The separate human benchmark freeze is untouched.

A future live comparison must record code/profile, exact input/request hash,
model, endpoint, request ID, tokens, latency and cost. Keep the old adverse output.
Use the evaluation specification's provider-separated metrics for broader
evaluation; do not disguise these development checks as held-out F1 or human
validation. Do not infer improvement merely because schema/reference tests pass.

No further Nebius/Tavily request, publication or paid deployment is authorized.
