# AgroField Agent — resumen completo para compartir con otra IA

> Snapshot verificable: 14 de septiembre de 2026. P0/P1 cerrados, freeze prehumano vigente, ensayo local seguro verificado y tres intentos reales controlados en Nebius documentados. Leer también `HANDOFF_PARA_OTRA_IA.md`, que contiene el contrato operativo y los comandos de reproducción.

## Resumen ejecutivo

AgroField Agent compite en Nebius x NVIDIA Global AI Hackathon 2026, track sugerido **Best Apps and Agents**. Fecha límite congelada: **30/10/2026 10:00 PDT / 14:00 Argentina**.

El producto no es un chatbot genérico. Resuelve un flujo estrecho: después de lluvia, granizo o viento, transforma una nota de campo por texto/voz en evidencia estructurada por lote, detecta omisiones críticas, prioriza tareas y bloquea decisiones sensibles hasta aprobación humana auditada.

Ya existe un MVP funcional con FastAPI, SQLite, interfaz móvil, extractor determinista local, adaptador Nebius/Nemotron guarded, memoria por lote, reglas de seguridad deterministas, aprobación humana y Tavily opcional restringido. Nada fue publicado. Hubo tres intentos reales y controlados bajo autorizaciones separadas: Playground, el harness CLI y la ruta `/api/analyze`. Ninguno produjo una extracción aceptada ni constituye benchmark; el tercero no demuestra que el modelo haya iniciado inferencia.

## Estado exacto

- Rama: `main` y working tree limpio antes de actualizar este resumen.
- HEAD verificado antes de esta actualización: `e0f0ad2` — `Fix raw Nemotron template arguments`; ejecutar `git log -1 --oneline` para obtener el commit posterior que contiene este archivo.
- Commits clave: MVP `32855c4`; Fase A/B `4390a4c`; gates `19ab37f`; P1 `1bd5a0e`; autorización `ff65472`; freeze prehumano `bee339e`; consentimiento obligatorio `5e4744c`; alcances anónimos `56286f7`; presentación local `4245d0e`; solicitud card-free enviada `2e14762`; modo grabación `7d88880`; smoke real Nebius `af29edf`; harness API seguro `395322f`; integración guarded en app `f4efc11`; llamada API documentada `3d5963b`; compatibilidad endurecida `911d786`; diagnóstico HTTP seguro `e8a926a`; prueba de unicidad `9cf6dd3`; wire format corregido `e0f0ad2`.
- Licencia: MIT.
- Tests: 68/68 aprobados; 23 cubren el harness y la ruta de aplicación Nebius con transporte simulado.
- Freeze vigente: 34/34 hashes válidos, versión `1.2.1-authorized-prehuman`.
- Gates del candidato local: 7/17 aprobados; `benchmark_validated: false` por diseño.
- `policy.py`: intacto desde el MVP.
- Autorización vigente: `AUTHORIZED_EMAIL_ONLY_PRIVATE_SETUP_ATTESTED`.
- Subestado operativo: `SUBMISSION_PREPARATION_WITH_UNVALIDATED_BENCHMARK`.
- Alcance original: el usuario puede enviar hasta 5 + 3 invitaciones por correo después del setup privado. En `DV-OUTREACH-001`, una dirección fue compartida transitoriamente y el envío fue asistido por IA; no se persistió PII en Git y no deben compartirse nuevos destinatarios.
- Slots de invitación enviados: 8/8 autorizados.
- Invitaciones: 5/5 de entrevista y 3/3 de revisión, según parte del usuario.
- Aceptaciones preliminares verbales: 5/5 para entrevista y cobertura de `R01`, `R02` y `A01`, según parte del usuario.
- Consentimientos informados escritos obligatorios válidos: 5/5 entrevistas y `R01`, `R02`, `A01`, según atestación saneada del custodio.
- Alcances de evidencia: 5/5 conclusiones agregadas, 5/5 escenarios saneados, resultados anónimos/agregados aceptados por `R01`, `R02`, `A01`; grabación 0/8.
- Setup privado: atestiguado por el usuario sin PII adicional el 2026-09-02.
- Entrevistas reales: 0.
- Aportes saneados del fundador con experiencia de dominio: 1, no independiente y fuera del benchmark.
- Revisiones humanas: 0/30 primarias y 0/10 secundarias.
- Revisiones humanas de salida: 0/30 primarias y 0/10 secundarias.
- Adjudicaciones humanas: 0/30.
- Nebius: 3 intentos de solicitud reales bajo autorizaciones independientes; Tavily: 0 llamadas.
- Smoke Nebius del 2026-09-14: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`, temperatura 0, JSON, máximo 256 tokens. La autenticación y conectividad funcionaron, pero el límite se consumió en razonamiento y la respuesta final quedó vacía (`Received empty assistant message`). No es un resultado del adaptador ni del benchmark.
- Smoke API AgroField del 2026-09-14: mismo modelo, `reasoning_effort: low`, máximo 1024 tokens, herramienta forzada, un POST y cero reintentos. El preflight calculó US$0,00122880 bajo un cap promocional de US$0,01. La API respondió, pero no devolvió exactamente un tool call; el contrato rechazó la salida. No es un resultado de `/api/analyze` ni del benchmark.
- Smoke live `/api/analyze` del 2026-09-14: mismo modelo, `reasoning_effort: none`, Tavily off, un POST local y cero reintentos. La ruta devolvió HTTP 503 después de un fallo upstream HTTP/transporte. La versión ejecutada no conservó estado upstream ni request ID; no se puede probar inferencia, no hubo salida ni se evaluó el tool contract.
- Perfil posterior al tercer intento: esquema compatible sin `minLength`/`uniqueItems`, validación client-side equivalente y diagnóstico saneado de estado HTTP/request ID/latencia. Pasa mocks, no fue ejecutado live y no debe presentarse como éxito Nemotron.
- Hallazgo raw/SDK: `extra_body` es una opción del cliente OpenAI que fusiona parámetros adicionales. Como AgroField usa `httpx` directamente, `chat_template_kwargs` debe ir en la raíz. `e0f0ad2` corrige y prueba esa forma; es la hipótesis principal del 503, no causalidad demostrada.
- Telemetría visible: 447 ms, 3 s y 88 t/s. El trial mostraba US$1 y el fallback se configuró en `Stop usage`. La consulta inmediata mostró `No usage` y ninguna transacción: cargo personal observado US$0, pero costo promocional real contabilizado no disponible.
- La clave temporal fue revocada y la lista de API keys quedó vacía. El secreto no está en Git y no debe reproducirse.
- Solicitud card-free: soporte respondió que el onboarding exige método de pago y que la verificación de tarjeta es de US$0; no ofreció un camino card-free.
- Repositorio/URL/video/submission públicos: no.

## Resultados reproducibles actuales

| Evaluación | Casos | F1 | Recall omisiones | No respaldadas | Seguridad | nDCG | Fallos | Validado |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Baseline local heredado | 12 | 0,9551 | 1,0000 | 0,0000 | 1,0000 | 1,0000 | 8 | No |
| Candidato local prehumano v1.2 | 30 | 0,9188 | 0,9714 | 0,0050 | 1,0000 | 0,9877 | 53 | No |

Proveedor de ambos: `local/deterministic-es-v0.1`. Task precision humana: no disponible. Son casos sintéticos y no son resultados Nemotron ni validación agronómica.

El candidato todavía falla el umbral de recall de omisiones críticas: `0,9714 < 0,98`. Ese dato es real para la referencia sintética provisional, pero no debe usarse para ajustar el holdout antes de obtener la referencia humana congelada.

## Qué cambió en el último incremento

Se agregó y verificó `python -m agrofield_agent --recording`. Cada arranque crea una base SQLite temporal nueva, fuerza `local/deterministic-es-v0.1`, anula las claves Nebius/Tavily durante el proceso, muestra `ENSAYO LOCAL · SINTÉTICO` y restaura el entorno al cerrar. La UI ahora ordena lotes por prioridad (`91 → 76 → 58 → 48`), exige escribir un revisor, traduce la decisión a `APROBADA/RECHAZADA`, evita una afirmación de vuelco que el extractor no respaldaba, versiona recursos estáticos y sirve favicon sin 404.

El recorrido se comprobó en navegador con una base fresca: nota incompleta bloqueada por `sample_points` y `water_duration_hours`; nota completa en `review_ready`; aprobación nominada; auditoría con `demo_seeded`, ambas evaluaciones y `task_approved`. Todas las rutas observadas respondieron 200. El guion quedó cronometrado a 2:42 y contiene una narración alternativa que identifica honestamente el proveedor local durante el ensayo.

La solicitud de acceso promocional sin tarjeta recibió respuesta: Nebius exige método de pago para completar onboarding. Bajo tres autorizaciones explícitas separadas se ejecutaron Playground, el harness guarded y la ruta real `/api/analyze`. Ninguna produjo una extracción aceptada; el tercer intento falló upstream antes de una salida observable. Las claves temporales fueron revocadas, la lista quedó vacía y no queda autorización para otra llamada.

Después del segundo fallo se implementó `911d786`. Nemotron Nano se fuerza sin razonamiento mediante `reasoning_effort: none` y `enable_thinking: false`; el esquema cierra propiedades y exige representaciones explícitas de ausencia; el parser vuelve a comprobar campos, citas y notas. Ese perfil se intentó una vez por `/api/analyze`, pero el fallo upstream impidió evaluarlo.

Después del tercer intento se implementó `e8a926a`, exclusivamente local. Los fallos HTTP futuros conservan solo estado, request ID seguro y latencia; los de transporte, solo latencia. Se retiraron `minLength` y `uniqueItems` del esquema enviado para reducir incompatibilidades opcionales, conservando las comprobaciones equivalentes del lado cliente. El preflight actual serializa 4.904 bytes, conserva el techo histórico de US$0,00122880 y se bloquea con código 2 sin autorización. No se abrió red para esta corrección.

La revisión de los ejemplos oficiales detectó después un error de wire format: el código raw enviaba `extra_body.chat_template_kwargs`, pero `extra_body` es el helper del SDK que fusiona parámetros en la raíz. `e0f0ad2` envía ahora `chat_template_kwargs` top-level. Con esa corrección, el preflight serializa 4.889 bytes, conserva US$0,00122880 y sigue bloqueándose sin red. La diferencia explica coherentemente el fallo, pero no lo confirma.

La base anterior conserva los siguientes controles:

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
- `docs/submission/nebius-smoke-run-2026-09-14.md`: registro verificable del smoke real en Playground, sus límites y la revocación de la clave.
- `docs/submission/nebius-api-smoke-run-2026-09-14.md`: registro de la única llamada real desde el harness de AgroField, su preflight, fallo de tool call y limpieza de credencial.
- `docs/submission/nebius-tool-contract-hardening-2026-09-14.md`: perfil corregido y evidencia local, explícitamente no validada live.
- `docs/submission/nebius-live-route-smoke-run-2026-09-14.md`: tercer intento por `/api/analyze`, fallo upstream, límites de afirmación y limpieza completa.
- `docs/submission/nebius-wire-format-correction-2026-09-14.md`: evidencia oficial, corrección raw/SDK y estado no validado live.

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

Existen tres intentos reales en Nebius y uno recorrió `/api/analyze`, pero todavía no hay una extracción aceptada ni métricas reales pareadas. El último intento falló upstream antes de que una salida del modelo fuera observable; por eso tampoco demuestra inferencia. El wire format probablemente incorrecto ya fue corregido y el perfil pasa 23 pruebas simuladas, pero aún no el endpoint real. Tampoco existen URL, repositorio o video públicos. La evidencia agronómica independiente sigue en cero; el aporte `FDI-001` es del fundador y no altera `benchmark_validated: false`.

## Próximo incremento de máximo impacto

El ensayo local de extremo a extremo y el harness de compatibilidad están estables. El harness está conectado a `/api/analyze` y tiene 23 pruebas simuladas, razonamiento desactivado, esquema cerrado, un techo conservador de costo, confirmación exacta, máximo de una solicitud por proceso, cero retries, diagnósticos saneados, validación literal y telemetría obligatoria. El payload raw corregido envía `chat_template_kwargs` top-level; su preflight local estimó US$0,00122880 con los precios históricos del 2026-09-14 y se bloqueó sin red por faltar autorización live. El próximo incremento externo de mayor ROI sería una llamada diagnóstica única por `/api/analyze` con `e0f0ad2`, pero no está autorizada: exigiría una nueva autorización, clave temporal y reconfirmación de precio, crédito y `Stop usage`. Tavily se conserva solo si una ablación autorizada demuestra valor trazable.

La revisión humana completa queda como mejora opcional de credibilidad, no como requisito oficial ni como logro realizado. No bajar sus gates ni describir el aporte del fundador como independiente.

## Texto listo para reanudar con otra IA

```text
Continúa AgroField Agent desde este repositorio. Lee completos y en este orden: README.md; docs/research/official-rules-freeze-2026-09-01.md; docs/architecture.md; docs/evaluation/evaluation-spec.md; docs/submission-readiness.md; docs/research/landscape-and-idea-matrix.md; docs/video-outline.md; HANDOFF_PARA_OTRA_IA.md; RESUMEN_COMPLETO_PARA_OTRA_IA.md; benchmark/agronomy_blind_v1/authorization/README.md; benchmark/agronomy_blind_v1/authorization/preflight-findings.md; benchmark/agronomy_blind_v1/authorization/authorization-decision-2026-09-02.md; benchmark/agronomy_blind_v1/authorization/email-outreach-pack.md; benchmark/agronomy_blind_v1/authorization/outreach-status-2026-09-02.md; benchmark/agronomy_blind_v1/authorization/post-acceptance-consent-pack.md; benchmark/agronomy_blind_v1/authorization/written-consent-status-2026-09-03.md; benchmark/agronomy_blind_v1/authorization/email-interview-fieldwork-pack.md; benchmark/agronomy_blind_v1/authorization/evidence-scope-status-2026-09-03.md; docs/submission/README.md; docs/submission/strategy-decision-2026-09-08.md; docs/submission/founder-domain-input-2026-09-08.md; docs/submission/devpost-draft.md; docs/submission/demo-runbook.md; docs/submission/rules-recheck-2026-09-08.md; docs/submission/nebius-smoke-attempt-2026-09-08.md; docs/submission/card-free-access-request.md; docs/submission/nebius-smoke-run-2026-09-14.md; docs/submission/nebius-api-compatibility-harness.md; docs/submission/nebius-api-smoke-run-2026-09-14.md; docs/submission/nebius-tool-contract-hardening-2026-09-14.md; docs/submission/nebius-live-route-smoke-run-2026-09-14.md; docs/submission/nebius-wire-format-correction-2026-09-14.md. Luego ejecuta git status, git log -10, pytest -q, ambos baselines y el freeze vigente.

Los cinco P0 y el P1 ya están cerrados. Hay 68/68 tests y freeze histórico 34/34. El benchmark tiene 0 entrevistas/revisiones humanas y `benchmark_validated=false`. Existe un aporte saneado del fundador (`FDI-001`) que solo informa diseño y no cuenta como validación independiente. El modo `--recording` fue verificado de extremo a extremo y siempre se identifica como local/sintético. Hubo tres intentos reales en Token Factory: Playground terminó sin mensaje final, el harness de AgroField respondió sin exactamente un tool call y `/api/analyze` devolvió 503 por un fallo upstream anterior a salida/contrato. Ninguno produjo una extracción aceptada; el tercero no demuestra inferencia. `e0f0ad2` corrige el wire format raw/SDK y el perfil tiene 23 pruebas simuladas, pero no fue ejecutado live. Las claves temporales quedaron revocadas y la lista vacía. No existe autorización para otra llamada Nemotron/Tavily. Antes de cualquier llamada nueva se exige autorización separada y límite concreto. No publicar, desplegar, subir video ni enviar la submission sin autorización expresa separada. Nunca atribuyas a humanos los fixtures ni modifiques `policy.py`.
```
