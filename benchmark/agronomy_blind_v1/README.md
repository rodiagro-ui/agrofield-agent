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
    case-annotation.template.json
    output-review.template.json
    adjudication.template.json
  data/
    cases.jsonl
    reviews/
  reports/
    local-candidate-2026-09-01.json
  freeze/
    manifest.json
```

## Flujo de trabajo

1. Obtener consentimiento y realizar 3–5 entrevistas sin mostrar primero la solución.
2. Sanitizar fuera del repositorio cualquier insumo; conservar aquí solo escenarios reescritos y anónimos.
3. Revisar los 30 casos de forma independiente usando la rúbrica.
4. Doble anotar los 10 casos prefijados como `double_review_required`.
5. Generar salidas sin revelar proveedor ni modelo.
6. Evaluar hechos, omisiones, prioridad y tareas en archivos separados por revisor.
7. Calcular desacuerdo bruto, Cohen’s kappa para etiquetas nominales y métricas de producto.
8. Adjudicar sin borrar el desacuerdo original.
9. Congelar archivos y hashes antes de una comparación Nemotron.

## Gates para declarar v1 validado

- 3–5 entrevistas consentidas, anonimizadas y resumidas.
- 30 casos con una revisión humana primaria completa.
- 10 casos con una segunda revisión independiente.
- Cero campos identificatorios o coordenadas exactas.
- Desacuerdo bruto y Cohen’s kappa reportados; no se exige ocultar un acuerdo bajo.
- Todos los conflictos adjudicados con justificación.
- `critical_omission_recall >= 0.98` y `decision_gate_safety == 1.0`.
- `unsupported_assertion_rate <= 0.01` y `task_precision >= 0.90`.
- Holdout sin usar para modificar extractor, reglas o umbrales.
- Manifiesto de freeze con hashes verificables.

## Verdad operativa actual

Los casos de `data/cases.jsonl` son candidatos sintéticos. Su referencia provisional sirve para desarrollar el arnés, no para afirmar validez agronómica. Hasta recibir revisión humana, las métricas deben llevar el rótulo `provisional_candidate_reference`.

No se ejecutará Nemotron ni Tavily durante este incremento.

## Comandos reproducibles

Evaluar el proveedor local contra la referencia candidata:

```bash
python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl
```

Generar un paquete ciego. El coordinador debe guardar fuera del repositorio el mapa entre alias y proveedor:

```bash
python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl \
  --blind-packet-out blind-packets.jsonl \
  --system-alias system-k7
```

Incorporar revisiones y exigir todos los gates:

```bash
python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl \
  --case-annotations benchmark/agronomy_blind_v1/data/reviews \
  --output-reviews benchmark/agronomy_blind_v1/data/reviews \
  --adjudications benchmark/agronomy_blind_v1/data/reviews/adjudications.jsonl \
  --require-validated
```

`--require-validated` termina con código distinto de cero mientras falten revisiones, adjudicaciones, task precision o acuerdo doble. Un resultado exitoso no cambia que el proveedor local y Nemotron deben reportarse por separado.

Verificar el freeze candidato y sus hashes normalizados:

```bash
python -m agrofield_agent.freeze benchmark/agronomy_blind_v1/freeze/manifest.json
```

El manifiesto congela artefactos candidatos y explícitamente conserva `human_validated: false`. Cuando lleguen las revisiones se deberá crear una nueva versión y un nuevo manifiesto; no se sobrescribe este freeze.
