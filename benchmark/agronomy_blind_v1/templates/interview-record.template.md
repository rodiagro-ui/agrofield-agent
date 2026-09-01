# Registro saneado de entrevista

> Guardar solo después de aplicar `protocol/consent-and-privacy.md`. No incluir notas originales.

Esta plantilla Markdown sirve para la toma y saneamiento fuera de Git. El único formato ingerible por el evaluador es `interview-record.template.json`, esquema `1.1.0-candidate`; debe contener tres resúmenes reescritos, consentimiento booleano, fecha ISO y una segunda revisión de privacidad en estado `passed`. Una plantilla vacía no cuenta.

## Control

- participant_id: `P__`
- role: `asesor | productor | scout | otro`
- experience_band: `0-4 | 5-9 | 10-19 | 20+`
- broad_region: `optional`
- consent_aggregated_insights: `yes | no`
- consent_sanitized_scenario: `yes | no`
- consent_anonymous_quote: `yes | no`
- recording_authorized: `yes | no`
- privacy_review_status: `pending | passed | failed`
- privacy_reviewer_id: `PR__`

## Episodio reescrito

- event_type:
- workflow_before_visit:
- information_channels:
- actor_observing:
- actor_deciding:
- missing_information_spontaneously_named:
- how_representativeness_was_checked:
- followup_or_return_visit:
- retained_audit_record:

## Costo y frecuencia por bandas

- frequency_band: `rare | few_per_season | monthly_in_season | weekly_in_season`
- consequence_band: `message_only | over_30_minutes | extra_visit | premature_decision_risk | other`
- people_involved_band: `1 | 2-3 | 4+`

## Evidencia y límites

- mandatory_fields_flooding:
- mandatory_fields_hail_wind:
- never_infer:
- appropriate_task_definition:
- premature_task_definition:
- unsafe_task_definition:
- priority_factors:
- useful_external_evidence:

## Evidencia contraria

- problem_not_recognized:
- blocking_friction:
- existing_solution_is_sufficient:
- reason_not_to_build:

## Reacción al concepto, preguntada al final

- useful:
- useless_or_annoying:
- trust_destroying_error:
- proof_required:
- preferred_work_surface:

## Codificación

- scenario_candidate: `yes | no`
- product_change_candidate:
- sanitized_scenario_summary:
- interviewer_notes_without_quotes:
