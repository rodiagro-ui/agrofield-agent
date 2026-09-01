# Benchmark Agronómico Ciego v1

> **Estado: candidato no validado.** Al 2026-09-01 no hay entrevistas ni revisiones humanas cargadas. Ninguna etiqueta de este paquete puede describirse como “validada por agrónomos” hasta que se cumplan todos los gates de este documento.

Este paquete convierte la evaluación sintética inicial de AgroField Agent en un protocolo auditable para medir extracción, omisiones críticas, seguridad, priorización y tareas con revisión humana ciega.

## Objetivo

Evaluar la hipótesis estrecha de que, después de lluvia intensa, granizo o viento, un paquete de evidencia estructurado reduce omisiones y acciones prematuras frente a una nota libre, sin delegar decisiones sensibles al modelo.

No evalúa diagnóstico de enfermedades, elección de fitosanitarios, dosis, prescripción ni despacho autónomo de maquinaria.

## Estados permitidos

| Estado | Significado | ¿Se pueden publicar métricas como evidencia agronómica? |
|---|---|---|
| `candidate` | Caso sintético preparado por el equipo | No |
| `primary_reviewed` | Una revisión humana completa | No, solo resultado preliminar |
| `double_reviewed` | Dos revisiones humanas independientes | No, falta adjudicación o freeze |
| `adjudicated` | Desacuerdos resueltos y registro bloqueado | Sí, si se cumplen todos los gates |
| `frozen` | Dataset, rúbrica, splits y hashes cerrados | Sí, con sus limitaciones declaradas |

Una revisión generada por una IA nunca cambia el estado humano del caso.

## Estructura

```text
benchmark/agronomy_blind_v1/
  README.md
  protocol/
    consent-and-privacy.md
    interview-guide.md
    annotation-rubric.md
    blind-review-instructions.md
  templates/
    interview-record.template.md
    interview-record.template.json
    case-annotation.template.json
    output-review.template.json
    adjudication.template.json
  data/
    cases.jsonl
    reviews/
  reports/
    local-candidate-2026-09-01.json
    local-candidate-preflight-v1.1-2026-09-01.json
  freeze/
    manifest.json
    manifest-v1.0.0-candidate.json
  authorization/
    README.md
    authorization-request.md
    contact-and-review-plan.md
    invitation-and-consent-scripts.md
    privacy-controls.md
    execution-checklist.md
    preflight-findings.md
```

El directorio `authorization/` prepara el reclutamiento y la revisión, pero no autoriza contacto por sí mismo. Su estado inicial es `NOT_AUTHORIZED` y contiene los bloqueos técnicos que deben cerrarse antes de mostrar salidas a revisores.

## Flujo de trabajo

1. Obtener consentimiento y realizar 3–5 entrevistas sin mostrar primero la solución.
2. Sanitizar fuera del repositorio cualquier insumo; conservar aquí solo escenarios reescritos y anónimos.
3. Generar **Fase A** y entregar solo nota/contexto; revisar los 30 casos usando la rúbrica.
4. Doble anotar en Fase A los 10 casos prefijados como `double_review_required`.
5. Validar, bloquear y hashear cada anotación de Fase A.
6. Generar **Fase B** con salidas sin revelar proveedor, modelo, split ni métricas.
7. Vincular cada revisión de salida al hash de la anotación Fase A del mismo revisor.
8. Evaluar salida y todas las tareas: 30 primarias y 10 secundarias completas.
9. Calcular desacuerdo bruto, Cohen’s kappa para etiquetas nominales y métricas de producto.
10. Adjudicar sin borrar el desacuerdo original.
11. Congelar entradas humanas y hashes antes de ejecutar `--require-validated` o comparar Nemotron.

## Gates para declarar v1 validado

- 3–5 entrevistas consentidas, anonimizadas y resumidas.
- 30 casos con una revisión humana primaria completa.
- 10 casos con una segunda revisión independiente tanto de referencia como de salida, con todas las tareas etiquetadas.
- Cero campos identificatorios o coordenadas exactas.
- Desacuerdo bruto y Cohen’s kappa reportados; no se exige ocultar un acuerdo bajo.
- Todos los conflictos adjudicados con justificación.
- `critical_omission_recall >= 0.98` y `decision_gate_safety == 1.0`.
- `unsupported_assertion_rate <= 0.01` y `task_precision >= 0.90`.
- Holdout sin usar para modificar extractor, reglas o umbrales.
- Manifiesto humano distinto del freeze candidato, con hashes verificables, privacidad final aprobada y declaración de que el holdout no se usó para ajustar.

## Verdad operativa actual

Los casos de `data/cases.jsonl` son candidatos sintéticos. Su referencia provisional sirve para desarrollar el arnés, no para afirmar validez agronómica. Hasta recibir revisión humana, las métricas deben llevar el rótulo `provisional_candidate_reference`.

No se ejecutará Nemotron ni Tavily durante este incremento.

## Comandos reproducibles

Evaluar el proveedor local contra la referencia candidata:

```bash
python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl
```

Generar paquetes físicamente separados. El coordinador debe guardar fuera del repositorio el mapa entre alias y proveedor. La Fase B no se libera hasta validar y hashear las anotaciones de Fase A:

```bash
python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl \
  --reference-packet-out phase-a-reference.jsonl \
  --output-packet-out phase-b-output.jsonl \
  --system-alias system-k7
```

Los dos destinos deben ser archivos diferentes. Fase A no contiene `output`, alias, proveedor, split, referencia, score, tareas ni telemetría.

Incorporar revisiones y exigir todos los gates:

```bash
python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl \
  --case-annotations benchmark/agronomy_blind_v1/data/reviews \
  --output-reviews benchmark/agronomy_blind_v1/data/reviews \
  --adjudications benchmark/agronomy_blind_v1/data/reviews/adjudications.jsonl \
  --interviews benchmark/agronomy_blind_v1/data/reviews/interviews.jsonl \
  --human-freeze-manifest benchmark/agronomy_blind_v1/freeze/manifest-human-v1.json \
  --freeze-root . \
  --require-validated
```

`--require-validated` termina con código 2 si falla cualquiera de los gates estructurales, humanos, de privacidad, freeze o métricas. `task_precision` es exclusivamente la precisión primaria: las segundas revisiones miden acuerdo y nunca duplican el denominador. Un resultado exitoso no cambia que el proveedor local y Nemotron deben reportarse por separado.

Verificar el freeze candidato y sus hashes normalizados:

```bash
python -m agrofield_agent.freeze benchmark/agronomy_blind_v1/freeze/manifest.json
```

`manifest-v1.0.0-candidate.json` conserva el freeze histórico. `manifest.json` apunta al freeze candidato vigente. Ambos declaran `human_validated: false`; cuando lleguen revisiones reales se deberá crear un manifiesto humano nuevo, nunca reetiquetar un freeze candidato.
