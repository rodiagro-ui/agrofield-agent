# AgroField Agent — resumen completo para compartir con otra IA

> Snapshot verificable: 1 de septiembre de 2026. Leer también `HANDOFF_PARA_OTRA_IA.md`, que contiene el contrato operativo y los comandos de reproducción.

## Resumen ejecutivo

AgroField Agent compite en Nebius x NVIDIA Global AI Hackathon 2026, track sugerido **Best Apps and Agents**. Fecha límite congelada: **30/10/2026 10:00 PDT / 14:00 Argentina**.

El producto no es un chatbot genérico. Resuelve un flujo estrecho: después de lluvia, granizo o viento, transforma una nota de campo por texto/voz en evidencia estructurada por lote, detecta omisiones críticas, prioriza tareas y bloquea decisiones sensibles hasta aprobación humana auditada.

Ya existe un MVP funcional con FastAPI, SQLite, interfaz móvil, extractor determinista local, adaptador Nebius/Nemotron preparado, memoria por lote, reglas de seguridad deterministas, aprobación humana y Tavily opcional restringido. Nada fue publicado ni ejecutado en servicios pagos.

## Estado exacto

- Rama: `main`; ejecutar `git log -1 --oneline` para el HEAD efectivo.
- Commits clave: MVP `32855c4`; Fase A/B `4390a4c`; gates `19ab37f`; freeze P0-closed `42f4e97`.
- Licencia: MIT.
- Tests: 41/41 aprobados.
- Freeze vigente: 32/32 hashes válidos.
- `policy.py`: intacto desde el MVP.
- Autorización de validación humana: `NOT_AUTHORIZED`.
- Personas contactadas: 0.
- Entrevistas reales: 0.
- Revisiones humanas: 0/30 primarias y 0/10 secundarias.
- Revisiones humanas de salida: 0/30 primarias y 0/10 secundarias.
- Adjudicaciones humanas: 0/30.
- Nebius/Tavily: 0 llamadas, US$0.
- Repositorio/URL/video/submission públicos: no.

## Resultados reproducibles actuales

| Evaluación | Casos | F1 | Recall omisiones | No respaldadas | Seguridad | nDCG | Fallos | Validado |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Baseline local heredado | 12 | 0,9551 | 1,0000 | 0,0000 | 1,0000 | 1,0000 | 8 | No |
| Candidato local v1.1 | 30 | 0,9188 | 0,9714 | 0,0050 | 1,0000 | 0,9877 | 53 | No |

Proveedor de ambos: `local/deterministic-es-v0.1`. Task precision humana: no disponible. Son casos sintéticos y no son resultados Nemotron ni validación agronómica.

## Qué cambió en el último incremento

Se cerraron los cinco bloqueos P0 de preflight:

1. Fase A de referencia y Fase B de salida están físicamente separadas.
2. Fase B exige el hash de la anotación Fase A bloqueada del mismo revisor.
3. Formularios incompletos o placeholder no cuentan.
4. `primary_task_precision` usa solo etiquetas primarias; las secundarias no duplican el denominador.
5. Se exigen 10 segundas revisiones completas tanto de referencia como de salida.
6. `benchmark_validated` depende de 17 gates explícitos: dataset completo, entrevistas, revisiones, adjudicación, acuerdo, privacidad, freeze y todos los umbrales.
7. `--require-validated` sale con código 2 ante cualquier fallo.

La suite incluye fallos independientes por cada gate, un caso que elimina una sola salida secundaria y un fixture positivo completo 30/10. Ese fixture está marcado expresamente como sintético de prueba y no constituye revisión humana.

Artefactos principales:

- `benchmark/agronomy_blind_v1/authorization/preflight-findings.md`: cierre verificable P0.
- `benchmark/agronomy_blind_v1/protocol/blind-review-instructions.md`: flujo Fase A/Fase B.
- `benchmark/agronomy_blind_v1/templates/`: esquemas `1.1.0-candidate`.
- `src/agrofield_agent/benchmarking.py`: validadores, locks, readiness, acuerdo y freeze humano.
- `src/agrofield_agent/evaluate.py`: métricas y 17 gates.
- `tests/test_benchmarking.py` y `tests/test_validation_gates.py`: pruebas del contrato.
- `benchmark/agronomy_blind_v1/freeze/manifest.json`: freeze candidato vigente.
- `benchmark/agronomy_blind_v1/freeze/manifest-v1.0.0-candidate.json`: freeze histórico preservado exactamente.
- `benchmark/agronomy_blind_v1/reports/local-candidate-preflight-v1.1-2026-09-01.json`: reporte local vigente.

## Reglas que no pueden romperse

- `policy.py` conserva autoridad sobre seguridad, evidencia, severidad y bloqueos.
- Separar hechos observados, inferencias y recomendaciones.
- No convertir ausencia de evidencia en evidencia de ausencia.
- Toda alerta debe apuntar a nota, regla o fuente identificable.
- Toda decisión sensible requiere aprobación nominada y auditoría.
- No inventar entrevistas, etiquetas, revisores, acuerdos o métricas humanas.
- No incorporar datos personales, nombres, establecimientos ni coordenadas reales.
- No contactar personas ni manejar datos reales sin autorización expresa.
- No publicar, desplegar, gastar créditos, llamar Nebius/Tavily, subir video ni enviar la submission sin autorización específica.
- Antes de cualquier servicio pago, pedir autorización y límite de gasto.

## Debilidad crítica residual

La evidencia externa sigue en cero. La ingeniería del benchmark ya evita contaminación obvia, pero el problema, la rúbrica y las tareas no fueron validados por asesores/productores ni agrónomos independientes. Por eso `benchmark_validated` sigue `false` y correr Nemotron ahora tendría menor ROI y riesgo de optimizar contra referencias circulares.

## Próximo incremento de máximo impacto

Solicitar autorización para la validación humana ya preparada:

- hasta 5 invitaciones privadas para obtener 3–5 entrevistas;
- hasta 3 profesionales para `R01`, `R02` y `A01`;
- canales uno a uno aprobados por el usuario;
- un recordatorio máximo;
- sin grabación ni compensación;
- custodio humano privado para identidades/contactos/notas crudas;
- Git e IA reciben solo datos saneados y anónimos;
- sin autorización implícita para Nebius, Tavily, publicación o gastos.

Solo después de autorización: 3–5 entrevistas → privacidad `PR01` → Fase A 30/10 → hashes → Fase B 30/10 → desacuerdo/kappa → adjudicación 30/30 → freeze humano → `--require-validated`. Luego solicitar autorización y presupuesto limitado para comparar local vs Nemotron. Tavily se evalúa después mediante ablación y se conserva solo si agrega valor trazable.

## Texto listo para reanudar con otra IA

```text
Continúa AgroField Agent desde este repositorio. Lee completos y en este orden: README.md; docs/research/official-rules-freeze-2026-09-01.md; docs/architecture.md; docs/evaluation/evaluation-spec.md; docs/submission-readiness.md; docs/research/landscape-and-idea-matrix.md; docs/video-outline.md; HANDOFF_PARA_OTRA_IA.md; RESUMEN_COMPLETO_PARA_OTRA_IA.md; benchmark/agronomy_blind_v1/authorization/README.md; benchmark/agronomy_blind_v1/authorization/preflight-findings.md. Luego ejecuta git status, git log -10, pytest -q, ambos baselines y el freeze vigente.

Los cinco P0 ya están cerrados. Hay 41/41 tests y freeze 32/32, pero 0 entrevistas/revisiones humanas y benchmark_validated=false. Nunca atribuyas a humanos los fixtures de prueba. No modifiques policy.py, no contactes personas ni manejes datos reales mientras siga NOT_AUTHORIZED, y no uses Nebius/Tavily, gastes, publiques, despliegues, subas video o envíes la submission sin autorización expresa. La prioridad es presentar el paquete de autorización y esperar decisión del usuario.
```
