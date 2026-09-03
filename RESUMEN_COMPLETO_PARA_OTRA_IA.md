# AgroField Agent — resumen completo para compartir con otra IA

> Snapshot verificable: 3 de septiembre de 2026. P0/P1 cerrados, consentimiento obligatorio atestiguado y freeze prehumano vigente. Leer también `HANDOFF_PARA_OTRA_IA.md`, que contiene el contrato operativo y los comandos de reproducción.

## Resumen ejecutivo

AgroField Agent compite en Nebius x NVIDIA Global AI Hackathon 2026, track sugerido **Best Apps and Agents**. Fecha límite congelada: **30/10/2026 10:00 PDT / 14:00 Argentina**.

El producto no es un chatbot genérico. Resuelve un flujo estrecho: después de lluvia, granizo o viento, transforma una nota de campo por texto/voz en evidencia estructurada por lote, detecta omisiones críticas, prioriza tareas y bloquea decisiones sensibles hasta aprobación humana auditada.

Ya existe un MVP funcional con FastAPI, SQLite, interfaz móvil, extractor determinista local, adaptador Nebius/Nemotron preparado, memoria por lote, reglas de seguridad deterministas, aprobación humana y Tavily opcional restringido. Nada fue publicado ni ejecutado en servicios pagos.

## Estado exacto

- Rama: `main` y working tree limpio antes de actualizar este resumen.
- HEAD verificado antes de esta actualización: `5e4744c` — `Record mandatory consent and prepare email interviews`; ejecutar `git log -1 --oneline` para obtener el commit posterior que contiene este archivo.
- Commits clave: MVP `32855c4`; Fase A/B `4390a4c`; gates `19ab37f`; P1 `1bd5a0e`; autorización `ff65472`; freeze prehumano `bee339e`; outreach completo `7f9b5a0`; paquete de consentimiento `627fceb`; consentimiento obligatorio `5e4744c`.
- Licencia: MIT.
- Tests: 44/44 aprobados.
- Freeze vigente: 34/34 hashes válidos, versión `1.2.1-authorized-prehuman`.
- Gates del candidato local: 7/17 aprobados; `benchmark_validated: false` por diseño.
- `policy.py`: intacto desde el MVP.
- Autorización vigente: `AUTHORIZED_EMAIL_ONLY_PRIVATE_SETUP_ATTESTED`.
- Subestado operativo: `EVIDENCE_SCOPE_COMPLETE_READY_FOR_EMAIL_INTERVIEWS`.
- Alcance original: el usuario puede enviar hasta 5 + 3 invitaciones por correo después del setup privado. En `DV-OUTREACH-001`, una dirección fue compartida transitoriamente y el envío fue asistido por IA; no se persistió PII en Git y no deben compartirse nuevos destinatarios.
- Slots de invitación enviados: 8/8 autorizados.
- Invitaciones: 5/5 de entrevista y 3/3 de revisión, según parte del usuario.
- Aceptaciones preliminares verbales: 5/5 para entrevista y cobertura de `R01`, `R02` y `A01`, según parte del usuario.
- Consentimientos informados escritos obligatorios válidos: 5/5 entrevistas y `R01`, `R02`, `A01`, según atestación saneada del custodio.
- Alcances de evidencia: 5/5 conclusiones agregadas, 5/5 escenarios saneados, resultados anónimos/agregados aceptados por `R01`, `R02`, `A01`; grabación 0/8.
- Setup privado: atestiguado por el usuario sin PII adicional el 2026-09-02.
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
| Candidato local prehumano v1.2 | 30 | 0,9188 | 0,9714 | 0,0050 | 1,0000 | 0,9877 | 53 | No |

Proveedor de ambos: `local/deterministic-es-v0.1`. Task precision humana: no disponible. Son casos sintéticos y no son resultados Nemotron ni validación agronómica.

El candidato todavía falla el umbral de recall de omisiones críticas: `0,9714 < 0,98`. Ese dato es real para la referencia sintética provisional, pero no debe usarse para ajustar el holdout antes de obtener la referencia humana congelada.

## Qué cambió en el último incremento

Se cerraron los cinco bloqueos P0 de preflight:

1. Fase A de referencia y Fase B de salida están físicamente separadas.
2. Fase B exige el hash de la anotación Fase A bloqueada del mismo revisor.
3. Formularios incompletos o placeholder no cuentan.
4. `primary_task_precision` usa solo etiquetas primarias; las secundarias no duplican el denominador.
5. Se exigen 10 segundas revisiones completas tanto de referencia como de salida.
6. `benchmark_validated` depende de 17 gates explícitos: dataset completo, entrevistas, revisiones, adjudicación, acuerdo, privacidad, freeze y todos los umbrales.
7. `--require-validated` sale con código 2 ante cualquier fallo.
8. El resultado vinculante usa todos los pares; se reporta una sensibilidad separada sin pares con exposición previa declarada.
9. Cruces globales primario/secundario o revisor/adjudicador bloquean readiness.
10. La autorización quedó registrada con límites 5 + 3, correo, usuario remitente/custodio, sin grabación ni compensación.
11. Existe un paquete de correos listo para que lo ejecute el usuario después de completar privadamente aviso, almacenamiento, retención y derechos.

La suite incluye fallos independientes por cada gate, un caso que elimina una sola salida secundaria y un fixture positivo completo 30/10. Ese fixture está marcado expresamente como sintético de prueba y no constituye revisión humana.

Artefactos principales:

- `benchmark/agronomy_blind_v1/authorization/preflight-findings.md`: cierre verificable P0/P1.
- `benchmark/agronomy_blind_v1/authorization/authorization-decision-2026-09-02.md`: autorización y exclusiones.
- `benchmark/agronomy_blind_v1/authorization/email-outreach-pack.md`: correos y gate privado.
- `benchmark/agronomy_blind_v1/authorization/outreach-status-2026-09-02.md`: primer envío saneado, desviación de control y mitigación.
- `benchmark/agronomy_blind_v1/authorization/post-acceptance-consent-pack.md`: aviso, consentimientos separados y gate posterior a las confirmaciones verbales.
- `benchmark/agronomy_blind_v1/authorization/written-consent-status-2026-09-03.md`: atestación saneada de consentimientos obligatorios y alcance aún pendiente.
- `benchmark/agronomy_blind_v1/authorization/email-interview-fieldwork-pack.md`: entrevista escrita en dos fases, saneamiento y parte agregado.
- `benchmark/agronomy_blind_v1/authorization/evidence-scope-status-2026-09-03.md`: atestación saneada que habilita el trabajo de campo por correo.
- `benchmark/agronomy_blind_v1/protocol/blind-review-instructions.md`: flujo Fase A/Fase B.
- `benchmark/agronomy_blind_v1/templates/`: esquemas `1.1.0-candidate`.
- `src/agrofield_agent/benchmarking.py`: validadores, locks, readiness, acuerdo y freeze humano.
- `src/agrofield_agent/evaluate.py`: métricas y 17 gates.
- `tests/test_benchmarking.py` y `tests/test_validation_gates.py`: pruebas del contrato.
- `benchmark/agronomy_blind_v1/freeze/manifest.json`: freeze candidato vigente.
- `benchmark/agronomy_blind_v1/freeze/manifest-v1.0.0-candidate.json`, `manifest-v1.1.0-candidate.json` y `manifest-v1.2.0-authorized-prehuman.json`: freezes históricos preservados.
- `benchmark/agronomy_blind_v1/reports/local-candidate-prehuman-v1.2-2026-09-02.json`: reporte local vigente.

## Reglas que no pueden romperse

- `policy.py` conserva autoridad sobre seguridad, evidencia, severidad y bloqueos.
- Separar hechos observados, inferencias y recomendaciones.
- No convertir ausencia de evidencia en evidencia de ausencia.
- Toda alerta debe apuntar a nota, regla o fuente identificable.
- Toda decisión sensible requiere aprobación nominada y auditoría.
- No inventar entrevistas, etiquetas, revisores, acuerdos o métricas humanas.
- No incorporar datos personales, nombres, establecimientos ni coordenadas reales.
- En adelante, solo el usuario contacta por correo dentro del alcance registrado; tras `DV-OUTREACH-001`, la IA no debe recibir nuevos destinatarios, PII ni notas crudas.
- No publicar, desplegar, gastar créditos, llamar Nebius/Tavily, subir video ni enviar la submission sin autorización específica.
- Antes de cualquier servicio pago, pedir autorización y límite de gasto.

## Debilidad crítica residual

La evidencia externa sigue en cero. La ingeniería del benchmark ya evita contaminación obvia, pero el problema, la rúbrica y las tareas no fueron validados por asesores/productores ni agrónomos independientes. Por eso `benchmark_validated` sigue `false` y correr Nemotron ahora tendría menor ROI y riesgo de optimizar contra referencias circulares.

## Próximo incremento de máximo impacto

El gate privado, el reclutamiento, el consentimiento escrito obligatorio y los alcances anónimos/agregados ya están completos por atestación saneada. Los 8 cupos están agotados y no deben sumarse destinatarios. La primera ronda neutral por correo está habilitada. No deben compartirse nombres, emails, firmas, organizaciones, localidades, calendarios o respuestas crudas. El próximo parte esperado es:

```text
ENTREVISTAS V1 — PARTE A SANEADO. No comparto PII.
Correos A enviados individualmente: [0–5]/5.
Respuestas A completas recibidas: [0–5]/5.
Respuestas que requieren una aclaración neutral: [conteo].
Retiros posteriores: [conteo].
PII enviada a la IA o Git: 0.
Contenido agronómico crudo enviado a la IA o Git: 0.
```

Después: Correo A neutral → Correo B de concepto → privacidad `DS01`/`PR01` → 3–5 registros válidos → Fase A 30/10 → hashes → Fase B 30/10 → desacuerdo/kappa/sensibilidad → adjudicación 30/30 → freeze humano → `--require-validated`. Bajo el alcance vigente, la recolección sustantiva está limitada al correo; una llamada o videollamada requiere ampliación expresa previa. Solo después del freeze humano se solicita autorización y presupuesto para Nemotron. Tavily se evalúa después mediante ablación y se conserva únicamente si agrega valor trazable.

## Texto listo para reanudar con otra IA

```text
Continúa AgroField Agent desde este repositorio. Lee completos y en este orden: README.md; docs/research/official-rules-freeze-2026-09-01.md; docs/architecture.md; docs/evaluation/evaluation-spec.md; docs/submission-readiness.md; docs/research/landscape-and-idea-matrix.md; docs/video-outline.md; HANDOFF_PARA_OTRA_IA.md; RESUMEN_COMPLETO_PARA_OTRA_IA.md; benchmark/agronomy_blind_v1/authorization/README.md; benchmark/agronomy_blind_v1/authorization/preflight-findings.md; benchmark/agronomy_blind_v1/authorization/authorization-decision-2026-09-02.md; benchmark/agronomy_blind_v1/authorization/email-outreach-pack.md; benchmark/agronomy_blind_v1/authorization/outreach-status-2026-09-02.md; benchmark/agronomy_blind_v1/authorization/post-acceptance-consent-pack.md; benchmark/agronomy_blind_v1/authorization/written-consent-status-2026-09-03.md; benchmark/agronomy_blind_v1/authorization/email-interview-fieldwork-pack.md; benchmark/agronomy_blind_v1/authorization/evidence-scope-status-2026-09-03.md. Luego ejecuta git status, git log -10, pytest -q, ambos baselines y el freeze vigente.

Los cinco P0 y el P1 ya están cerrados. Hay 44/44 tests y freeze histórico 34/34. El usuario atestigua consentimiento escrito y alcances contables para 5/5 entrevistas y R01/R02/A01; grabación 0/8. Hay 0 entrevistas/revisiones humanas y benchmark_validated=false. La siguiente acción autorizada es enviar individualmente el Correo A neutral de `email-interview-fieldwork-pack.md`, exclusivamente por el usuario y sin compartir respuestas crudas. El setup privado fue atestiguado sin PII adicional y no quedan cupos para nuevos destinatarios. Una dirección real ya fue compartida transitoriamente para `I01`; no revelar nuevos identificadores ni persistir PII en Git. Nunca atribuyas a humanos los fixtures. No modifiques policy.py ni uses Nebius/Tavily, gastes, publiques, despliegues, subas video o envíes la submission sin autorización expresa separada.
```
