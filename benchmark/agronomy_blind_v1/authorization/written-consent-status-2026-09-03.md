# Estado saneado de consentimiento escrito — 2026-09-03

> Registro operativo posterior al freeze `1.2.1-authorized-prehuman`. No forma parte de ese freeze, no contiene PII y no convierte una atestación privada en evidencia agronómica.

## Atestación recibida

El usuario, custodio privado de identidades y correos, confirmó explícitamente el 2026-09-03 el parte saneado solicitado en `post-acceptance-consent-pack.md`:

- entrevistas con consentimiento escrito obligatorio válido: **5/5**;
- roles con consentimiento escrito obligatorio válido: **`R01`, `R02` y `A01`**;
- consentimientos ambiguos o incompletos: **0**;
- retiros o rechazos acumulados: **0**;
- contenido sustantivo recogido antes del consentimiento: **0**;
- PII incorporada a Git o enviada a la IA: **0**;
- datos agronómicos reales enviados a Git o a la IA: **0**.

La IA no vio ni auditó respuestas, cabeceras, firmas o identidades. Los conteos son una atestación saneada del custodio y las pruebas identificables permanecen fuera del repositorio.

## Alcances que no se infieren

La confirmación anterior cubre los consentimientos **obligatorios**: comprensión y participación para entrevistas; comprensión, participación e independencia para los tres roles profesionales. No informa cuántas personas aceptaron los alcances separados necesarios para que sus registros cuenten en el benchmark:

- `consent_aggregated_insights: true`;
- `consent_sanitized_scenario: true`;
- `consent_to_anonymous_results: true` para `R01`, `R02` y `A01`.

Esos alcances pueden haberse respondido en privado, pero no se presumen. Tampoco se presume consentimiento para citas, publicación, grabación, llamada o videollamada. La publicación sigue bloqueada aunque todos los alcances opcionales sean `SÍ`.

## Estado operativo

`MANDATORY_WRITTEN_CONSENT_COMPLETE_EVIDENCE_SCOPE_PENDING`

- Entrevistas realizadas: **0/5**.
- Registros de entrevista saneados y aprobados por `PR01`: **0/5**.
- Revisiones de referencia: **0/30 primarias, 0/10 secundarias**.
- Revisiones de salida: **0/30 primarias, 0/10 secundarias**.
- Adjudicaciones: **0/30**.
- `benchmark_validated`: **false**.

El consentimiento obligatorio permite participar. Para producir evidencia que el evaluador pueda contar, el custodio debe confirmar además, solo por conteos/códigos, los alcances de uso anónimo indicados arriba. Bajo la autorización vigente, toda recolección sustantiva se limita al correo. Una llamada o videollamada requiere ampliación expresa previa y continúa sin grabación.

## Próximo parte mínimo

```text
ALCANCES DE EVIDENCIA V1 — ACTUALIZACIÓN SANEADA. No comparto PII.
Entrevistas con consentimiento para conclusiones agregadas: [0–5]/5.
Entrevistas con consentimiento para escenario saneado: [0–5]/5.
R01 consiente resultados anónimos/agregados: SÍ / NO.
R02 consiente resultados anónimos/agregados: SÍ / NO.
A01 consiente resultados anónimos/agregados: SÍ / NO.
Consentimiento para grabación: 0/8.
PII enviada a la IA o Git: 0.
```

No informar quién aceptó citas ni vincular una persona con un código de participante. Si menos de tres entrevistas aceptan ambos alcances de evidencia, detener la incorporación al benchmark y revisar el plan con el usuario.
