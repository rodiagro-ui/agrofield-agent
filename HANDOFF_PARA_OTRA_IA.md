# AgroField Agent — handoff operativo para otra IA

> Snapshot: 15 de septiembre de 2026, tras preparar el candidato semántico v2. Repositorio local, sin publicación ni despliegue. La primera extracción histórica de Nemotron fue aceptada con calidad insuficiente; v2 aún no fue llamado. Las cuatro autorizaciones de solicitud única están consumidas.

## Ubicación y estado

El repositorio Git es outputs/agrofield-agent dentro del workspace nebius-nvidia-agrofield-agent; ejecutar todos los comandos desde esa raíz, no desde el directorio padre.

- Rama: main. Ejecutar git status y git log para conocer HEAD y cambios efectivos.
- MVP base: 32855c4; política determinista intacta desde ese commit.
- Fase A/B: 4390a4c; gates humanos: 19ab37f; P1 de exposición/roles: 1bd5a0e.
- Freeze prehumano vigente: bee339e; 34/34 hashes, versión 1.2.1-authorized-prehuman.
- Preparación honesta de presentación: 4245d0e; ensayo local seguro: 7d88880.
- Harness guarded: 395322f; integración en app: f4efc11.
- Perfil sin razonamiento: 911d786; diagnósticos: e8a926a; wire raw/SDK: e0f0ad2.
- Anclaje por IDs de fuente: 1c432ed. Este es el commit ejecutado en la primera extracción aceptada.
- Auditoría offline y registro saneado de la llamada: 8d994c4. Consultar git log para el commit posterior de actualización documental.
- Instrucciones semánticas v2 y validación numérica: 6d7a5a8; casos/checker/freeze de desarrollo: ab339dc.
- Licencia MIT.
- 124 pruebas aprobadas: incluyen 37 pruebas Nebius simuladas, nueve de fuentes, tres de auditoría guardada y 30 del perfil/referencias de desarrollo.
- Cero cambios en policy.py, extractor local o benchmark congelado durante este incremento.
- Hash SHA-256 canónico de policy.py: e659fb913cc7526d4c9673e7ce6460ba83abce310a9fe8e0d94dbd3900d9938b.

## Lectura obligatoria

Leer completos y en este orden:

1. README.md
2. docs/research/official-rules-freeze-2026-09-01.md
3. docs/architecture.md
4. docs/evaluation/evaluation-spec.md
5. docs/submission-readiness.md
6. docs/research/landscape-and-idea-matrix.md
7. docs/video-outline.md
8. HANDOFF_PARA_OTRA_IA.md
9. RESUMEN_COMPLETO_PARA_OTRA_IA.md
10. benchmark/agronomy_blind_v1/authorization/README.md
11. benchmark/agronomy_blind_v1/authorization/preflight-findings.md
12. docs/submission/README.md
13. docs/submission/nebius-source-anchor-run-2026-09-14.md
14. docs/submission/nebius-semantic-candidate-2026-09-15.md
15. fixtures/development/semantic_v2/README.md

Para trabajo Nebius: leer además nebius-api-compatibility-harness.md, nebius-source-anchors-2026-09-14.md y los registros de intentos anteriores dentro de docs/submission/.
Para evidencia humana: leer los estados, consentimiento, alcance y fieldwork pack enlazados desde authorization/README.md.
Para entrega: leer strategy-decision-2026-09-08.md, founder-domain-input-2026-09-08.md, rules-recheck-2026-09-08.md, devpost-draft.md y demo-runbook.md dentro de docs/submission/.

Después reproducir sin servicios externos:

    git status --short --branch
    git log --oneline -12
    .\.venv\Scripts\python.exe -m pytest -q
    .\.venv\Scripts\python.exe -m agrofield_agent.evaluate fixtures/eval_cases.jsonl
    .\.venv\Scripts\python.exe -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl
    .\.venv\Scripts\python.exe -m agrofield_agent.freeze benchmark/agronomy_blind_v1/freeze/manifest.json --root .
    .\.venv\Scripts\python.exe -m agrofield_agent.smoke_audit
    .\.venv\Scripts\python.exe -m agrofield_agent.semantic_preflight
    .\.venv\Scripts\python.exe -m agrofield_agent.freeze fixtures/development/semantic_v2/manifest.json --root .

## Producto y límites de confianza

AgroField Agent coordina recorridas de soja después de lluvia intensa, viento o granizo. FastAPI, SQLite e interfaz móvil convierten notas de texto o voz del navegador en observaciones, omisiones, prioridades y tareas pendientes. Memoria por lote y auditoría conservan trazabilidad. No es un prescriptor autónomo.

El modo local usa deterministic-es-v0.1. El modo Nebius de la aplicación usa un adaptador guarded: una solicitud por proceso, cero retries, autorización/cap/precios obligatorios, esquema cerrado, fuentes por IDs, citas resueltas contra la nota original y telemetría. La app nunca permite al modelo desactivar policy.py.

El anclaje de fuentes evita citas inventadas o parafraseadas: no garantiza que la frase respalde el valor elegido. La prueba real documentó precisamente ese límite.

El perfil actual es source-anchors-es-v2-semantic-candidate. Añade definiciones explícitas de los 12 campos, distingue tiempos/porcentajes, negación y alcance por lote, y rechaza cantidades negativas/no finitas. Esto no reemplaza un validador semántico ni demuestra mejora del modelo. Su único estado es candidato probado localmente, no resultado live.

El modo python -m agrofield_agent --recording fuerza local, desactiva credenciales externas, usa SQLite temporal y muestra ENSAYO LOCAL · SINTÉTICO. Su ensayo fue verificado de extremo a extremo. No es evidencia de una demo Nemotron. Tavily es opcional, restringido a fuentes permitidas y nunca fue llamado.

## Resultados de referencia: solo proveedor local

| Métrica | 12 casos sintéticos | 30 casos candidatos sintéticos |
|---|---:|---:|
| Precisión | 0.9884 | 0.9851 |
| Recall | 0.9239 | 0.8609 |
| F1 micro | 0.9551 | 0.9188 |
| Recall de omisiones | 1.0000 | 0.9714 |
| Afirmaciones no respaldadas | 0.0000 | 0.0050 |
| Cobertura de citas | 1.0000 | 1.0000 |
| Seguridad de bloqueo | 1.0000 | 1.0000 |
| Integridad de aprobación | 1.0000 | 1.0000 |
| nDCG | 1.0000 | 0.9877 |
| Fallos adversos | 8 | 53 |

Proveedor de ambas columnas: local/deterministic-es-v0.1. Task precision humana: no disponible. Benchmark candidato: 7/17 gates y benchmark_validated false. El recall de omisiones del candidato tampoco alcanza su umbral 0.98. Estos números no se atribuyen a Nemotron ni a agrónomos.

## Cuatro solicitudes reales Nebius, cronología correcta

Modelo en todos los intentos: nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B. Cada solicitud tuvo autorización separada; ninguna fue una evaluación de benchmark.

1. Playground: el presupuesto de 256 tokens se agotó en razonamiento y no hubo mensaje final.
2. Harness CLI: API respondió, pero no exactamente un tool call; salida rechazada.
3. Ruta local /api/analyze: HTTP 503, non-literal evidence quote for: event_type. Alcanzó validación de evidencia; NO fue un fallo upstream de conexión. La respuesta rechazada no fue retenida, por lo que no se conoce la causa textual.
4. Tras wire format y source IDs, primera observación aceptada: HTTP 200, 2026-09-14 23:03 UTC, commit 1c432ed. FastAPI TestClient in-process con HTTPS real a Nebius; no despliegue público ni recorrido browser E2E.

Resultado del cuarto intento:

- Una nota sintética de desarrollo; una solicitud, cero reintentos.
- Latencia: 7,591.67 ms; 2,288 tokens de entrada y 311 de salida.
- Preflight: 5,885 bytes; techo US$0.00122880 con precios observados US$0.06/M entrada y US$0.24/M salida.
- Costo estimado desde uso: US$0.00021192, no factura contabilizada.
- Trial visible US$1, 29 días; Usage stops after the trial; saldo de cuenta cero antes de llamar.
- Consulta posterior redondeada sin cargo personal visible; no demuestra costo exacto cero.
- Clave temporal revocada; lista de claves verificada vacía; variables/portapapeles limpiados y helper transitorio eliminado.
- Política blocked; una tarea pendiente, ninguna aprobada ni ejecutada.
- Todas las citas no vacías eran literales.
- Calidad contra referencia sintética de desarrollo: 4/8 campos observados correctos, tres omisiones, un evento incorrecto y una condición general sin respaldo. Local: 8/8 en esa nota.
- Las omisiones del modelo fueron edad del evento (18 h), agua parada (35%) y duración (14 h). No eran omisiones reales de la nota.
- El diagnóstico examina 12 campos, incluidos cuatro que deberían permanecer desconocidos. No se mezcla con F1 del benchmark.
- Contrato aceptado no equivale a calidad aceptable. No hay superioridad Nemotron demostrada.

Registro saneado: docs/submission/evidence/nebius-source-anchor-smoke-2026-09-14.json.
Referencia sintética: fixtures/nebius_smoke_reference.json; sus valores ya estaban en tests antes de la llamada, no son etiquetas humanas.
Auditoría reproducible: python -m agrofield_agent.smoke_audit; sin red, con hash de la nota.
Reporte interpretado: docs/submission/nebius-source-anchor-run-2026-09-14.md.

## Nuevo paquete de desarrollo v2, separado del benchmark

- fixtures/development/semantic_v2/cases.jsonl: 20 notas nuevas con referencias explícitamente escritas por IA; split development en todas, no humanas y no holdout.
- Casos de tiempos separados, porcentajes con distinto denominador, granizo negado, tormenta inespecífica, condición desconocida, otro lote, plantas/puntos, unidades, contradicciones, cero verificado y órdenes incrustadas.
- semantic_preflight valida forma/citas de las referencias y presupuesto de los requests: no crea salidas del modelo ni calcula calidad.
- preflight.json conserva fingerprints por nota/request y cobertura de campos observados/desconocidos. nemotron_quality null; benchmark_validated false.
- manifest.json congela ocho archivos del perfil/referencias/checker; 8/8 verificados. No sustituye ni modifica el freeze humano candidato de 34 archivos.
- Payload de la nota smoke: 9.776 bytes; máximo de los 20 casos: 9.999. Techo preventivo por solicitud sin cambios: US$0,00122880 con precios históricos. No es un precio vigente ni nueva autorización.
- Los prompts más largos podrían aumentar tokens/latencia; ninguna mejora de calidad o rendimiento fue medida.
- Mantener ambos freezes y el resultado adverso anterior. Versionar cambios futuros de perfil/referencias; no editar referencias después de observar resultados para mejorar el puntaje.

## Estado humano, privacidad y estrategia

- Entrevistas completadas: 0.
- Revisiones primarias: 0/30; dobles de referencia: 0/10.
- Revisiones de salida: 0/30 primarias, 0/10 secundarias.
- Adjudicaciones: 0/30. Acuerdo y task precision humanos: no disponibles.
- Aporte del fundador: uno saneado, no independiente, fuera del benchmark.
- Invitaciones enviadas según atestación del usuario: 5/5 entrevistas y 3/3 revisión; no se autorizan más destinatarios.
- Aceptaciones, consentimientos escritos privados y alcances agregados/anónimos: atestiguados por usuario para 5/5 y R01/R02/A01. No equivalen a entrevistas o anotaciones terminadas.
- Remitente y custodio privado: usuario. Solo correo; sin grabación ni compensación.
- Estado humano registrado: AUTHORIZED_EMAIL_ONLY_PRIVATE_SETUP_ATTESTED.
- Desviación histórica DV-OUTREACH-001 registrada; la IA no recibe nuevos destinatarios, identidades ni notas crudas.
- Subestado: SUBMISSION_PREPARATION_WITH_UNVALIDATED_BENCHMARK.

El usuario decidió preparar una presentación lean sin esperar el protocolo humano completo. No bajar los gates ni relabelar evidencia. La revisión humana independiente sigue siendo una debilidad de credibilidad, aunque no sea requisito oficial de submission.

## P0/P1 y freeze que deben preservarse

- Fase A sin salida del sistema; Fase B separada y ligada al hash de A del mismo revisor.
- Formularios incompletos/placeholder no cuentan.
- primary_task_precision usa solo revisiones primarias.
- Exige 30 primarias y diez dobles completas de referencia y salida.
- benchmark_validated depende de 17 gates; --require-validated sale 2 ante fallo.
- Acuerdo vinculante conserva todos los pares; sensibilidad de exposición se informa aparte.
- Cruces globales entre primario, secundario y adjudicador bloquean validación.
- Fixtures positivos 30/10 son pruebas sintéticas, nunca evidencia humana.

manifest.json es 1.2.1-authorized-prehuman, candidate_only y human_validated false; 34 hashes. Los conteos de autorización/contacto del manifiesto describen el momento histórico del freeze, no el estado actual. Los manifests anteriores se preservan. Un freeze humano deberá ser nuevo; no reescribir este snapshot.

## Reglas y permisos

No modificar ni debilitar policy.py. Separar hechos, inferencias y recomendaciones; toda alerta trazable, toda decisión sensible con aprobación nominada y auditoría. Desconocido no significa ausente. No inventar etiquetas, personas, revisiones, acuerdos o métricas.

Cero secretos, PII, establecimientos reales o coordenadas exactas en Git. Solo registros saneados con el alcance autorizado.

Las cuatro autorizaciones Nebius de una solicitud están consumidas. No llamar de nuevo ni crear otra clave sin autorización específica y cap concreto. No Tavily, gastos, publicación de repo, despliegue, video ni submission sin autorización. Verificar precio, crédito y Stop usage antes de una llamada autorizada; detenerse ante cobro o crédito insuficiente.

## Próximo incremento de mayor impacto

El candidato semántico está preparado y congelado. La siguiente evidencia de mayor valor sería una nueva solicitud diagnóstica sobre la misma nota de desarrollo histórica, con autorización separada. Comparar los 12 campos y conservar tanto aciertos como errores, tokens/latencia/costo; no basta HTTP 200. Una repetición perfecta tampoco constituye benchmark ni valida toda la demo.

Sin esa autorización, solo trabajo local. No repetir solicitudes con permisos ya consumidos ni reconstruir respuestas supuestas. Preservar policy.py, holdout y evidencia adversa. Antes de presentar, faltan calidad medida de v2, demo completa Nemotron, evaluación más amplia y URL/repo/video públicos autorizados.

Fecha límite de las bases congeladas: 30/10/2026 10:00 PDT / 14:00 Argentina. Última revisión oficial registrada: 08/09/2026; no se hizo una nueva comprobación de bases en este incremento.
