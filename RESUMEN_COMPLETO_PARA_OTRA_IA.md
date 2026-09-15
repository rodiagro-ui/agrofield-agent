# AgroField Agent — resumen actualizado para compartir

> 15 de septiembre de 2026, nuevo smoke autorizado pero pausado antes de inferencia por un fallo local de transferencia; clave revocada. V2 sigue sin resultado live. Nada público. Este archivo informa estado; no concede permisos de gasto ni publicación.

## Qué estamos construyendo

AgroField Agent es un coordinador de recorridas de soja posteriores a lluvia, viento o granizo, para Nebius x NVIDIA Global AI Hackathon 2026. Convierte notas por texto o voz en observaciones trazables, omisiones críticas, prioridades y tareas con aprobación humana. No es un chatbot genérico ni un prescriptor autónomo.

Track previsto: Best Apps and Agents. Tavily solo si demuestra valor medible y trazable. Fecha límite congelada: 30/10/2026 10:00 PDT / 14:00 Argentina. La última revisión oficial documentada fue el 08/09; no se volvió a verificar durante este incremento.

Repositorio real: outputs/agrofield-agent dentro del workspace nebius-nvidia-agrofield-agent. Licencia MIT. Consultar git status y git log desde esa raíz.

Commits recientes: 1c432ed (anclaje de fuentes y perfil usado en la llamada aceptada) y 8d994c4 (evidencia saneada y auditoría offline). El resumen documental se guarda después; consultar git log para HEAD efectivo.

Nuevo incremento: 6d7a5a8 (definiciones semánticas y rechazo de cantidades inválidas) y ab339dc (20 casos de desarrollo, preflight sin red y freeze separado).

Último incremento técnico: 27ca97b (preflight de navegador sin credenciales y nueve tests). El registro documental de la pausa se guarda después; consultar git log para HEAD efectivo.

## Avance implementado

- MVP FastAPI + SQLite + interfaz móvil, memoria por lote y auditoría.
- Captura por texto/voz del navegador y extractor determinista local.
- Política determinista de seguridad intacta desde MVP 32855c4.
- Tareas pendientes hasta aprobación humana explícita.
- Adaptador guarded Nebius/Nemotron con presupuesto, una solicitud por proceso, cero reintentos y telemetría.
- Fuentes por IDs resueltas a citas originales en commit 1c432ed; nunca confiar en citas inventadas por el modelo.
- Ensayo local reproducible: python -m agrofield_agent --recording, base temporal, credenciales externas desactivadas y etiqueta local/sintética.
- Benchmark candidato de 30 casos, Fase A/B separadas, P0/P1 cerrados, 17 gates y freeze inmutable.
- Borrador Devpost, guion de menos de tres minutos, controles de afirmaciones y documentación de entrega.
- Nueva auditoría offline de la respuesta real, con fallos preservados y referencia sintética identificada.
- Perfil source-anchors-es-v2-semantic-candidate: los 12 campos ahora tienen definiciones explícitas; distingue tiempos, porcentajes, negación, otros lotes y condición del cultivo. No es una mejora real medida todavía.
- Validación reforzada contra cantidades negativas/no finitas, sin reintentos ni sustitución por el extractor local.
- 20 casos nuevos escritos por IA, todos de desarrollo y fuera del benchmark; referencias y requests congelados en ocho archivos. No se inventó revisión humana ni respuesta del modelo.

## Verificación local actual

133 pruebas aprobadas; 34/34 hashes del benchmark y 8/8 del candidato de desarrollo válidos. policy.py intacto. Incluyen nueve nuevos tests del diagnóstico local de transferencia; no son métricas de calidad Nemotron.

| Métrica | Baseline local, 12 casos | Candidato local, 30 casos |
|---|---:|---:|
| F1 extracción | 0.9551 | 0.9188 |
| Recall omisiones críticas | 1.0000 | 0.9714 |
| No respaldadas | 0.0000 | 0.0050 |
| Seguridad de bloqueo | 1.0000 | 1.0000 |
| nDCG | 1.0000 | 0.9877 |
| Fallos adversos | 8 | 53 |

Ambas columnas: local/deterministic-es-v0.1, datos sintéticos. Candidato: 7/17 gates, benchmark_validated false. Recall candidato por debajo del umbral 0.98. Ninguna cifra de esta tabla es Nemotron ni validación humana.

## Lo que ocurrió realmente con Nemotron

Cuatro solicitudes reales el 14/09, cada una bajo autorización limitada independiente:

1. Playground: agotó el presupuesto de razonamiento sin mensaje final.
2. CLI de AgroField: no devolvió exactamente un tool call; rechazada.
3. /api/analyze: cita de event_type no literal; HTTP 503 local. Llegó al validador. Las versiones anteriores del resumen que lo llamaban fallo upstream estaban equivocadas.
4. Source IDs: primera observación aceptada, HTTP 200. Ruta /api/analyze con FastAPI TestClient en proceso y HTTPS real a Nebius, no una demo pública/browser completa.

Cuarto intento, modelo nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B:

- 1 solicitud, 0 reintentos.
- 7.59 segundos; 2,288 tokens entrada / 311 salida.
- US$0.00021192 estimados desde tokens y precios observados; no factura definitiva.
- Tope autorizado US$0.01 promocional, US$0 personal. Preflight US$0.00122880.
- Crédito y Stop usage verificados antes de llamar; sin cargo personal visible en consulta inmediata redondeada.
- Clave temporal revocada, lista de claves vacía y material temporal limpiado.
- Política bloqueada y una tarea pendiente; ninguna ejecución automática.

**Calidad insuficiente:** Nemotron acertó 4 de los 8 campos observados esperados; omitió edad del evento, porcentaje de agua y duración; clasificó mal el evento y añadió una condición general sin respaldo. Local acertó 8/8 en esa misma nota. Las citas eran literales, pero algunas no respaldaban el valor. Pasar formato no equivale a comprender bien la nota.

Esta comparación usa un único caso sintético de desarrollo con referencia del desarrollador: no es holdout, evidencia agronómica ni prueba estadística de superioridad. No se ejecutó el benchmark con Nemotron.

Evidencia y reproducción:

- docs/submission/nebius-source-anchor-run-2026-09-14.md
- docs/submission/evidence/nebius-source-anchor-smoke-2026-09-14.json
- fixtures/nebius_smoke_reference.json
- python -m agrofield_agent.smoke_audit — sin red ni créditos, compara respuesta guardada y extractor local.

V2 no hizo otra llamada: total histórico sigue en cuatro. Su preflight local usa 9.776 bytes para la nota smoke y como máximo 9.999 para los 20 casos. El 15/09 se revalidaron precios US$0.06/M entrada y US$0.24/M salida, promoción visible US$1.00/28 días y Stop usage. Techo preventivo US$0.00122880; no se consumió nuevo crédito de inferencia. El prompt más largo puede aumentar costo/latencia; aún no fue medido.

Nuevo paquete: fixtures/development/semantic_v2/README.md y docs/submission/nebius-semantic-candidate-2026-09-15.md. Reproducción: python -m agrofield_agent.semantic_preflight. Reporta nemotron_quality null y benchmark_validated false; valida referencias, no predicciones.

## Pausa local del 15/09 y siguiente control

El usuario sí autorizó una nueva llamada Nano, 0 reintentos, máximo US$0.01 promocional/US$0 personal y clave temporal, exigiendo pausa ante anomalías. No consumió su cupo de inferencia: el formulario local rechazó la transferencia (HTTP 403) antes de invocar AgroField/Nebius. Se revocó la clave y verificó la lista vacía; ejecutor, base temporal, helpers y variables sensibles limpiados. No atribuir este fallo a Nemotron.

Causa reproducida con datos ficticios: Referrer-Policy no-referrer del propio helper produce Origin:null en un POST normal; el guard lo rechaza. same-origin conserva el origen local esperado y permite mantener el rechazo de null/orígenes ajenos. Se añadió python -m agrofield_agent.handoff_preflight: diagnóstico reproducible que NO lee cuerpos, claves ni ejecuta API. Ensayo real de navegador y nueve tests aprobados. Un fallo previo de limpieza SQLite del helper en Windows también se corrigió y comprobó localmente; no se cambió Repository ni policy.py.

Registro detallado: docs/submission/nebius-semantic-preflight-pause-2026-09-15.md. La llamada real permanece pausada hasta reanudación explícita. Antes de crear otra clave, ensayar todo el futuro runner mediante navegador y transporte simulado; después revalidar facturación. No aceptar Origin:null como atajo.

## Evidencia humana: estado honesto

Cero entrevistas completadas; cero revisiones primarias/dobles/de salida y cero adjudicaciones. No hay kappa ni task precision humanos. Existe un aporte saneado del fundador, no independiente y fuera del benchmark.

El usuario atestiguó 5/5 invitaciones de entrevista y 3/3 de revisión enviadas, aceptaciones y consentimientos escritos privados con alcances agregados/anónimos para R01/R02/A01. Eso no equivale a haber recibido resultados.

Solo el usuario es remitente/custodio; solo correo, sin grabación ni compensación. No se reciben PII ni notas crudas. No hay permiso para destinatarios adicionales.

Se decidió preparar una submission lean sin esperar el protocolo humano completo, declarando esta limitación. No se alteraron ni rebajaron los gates del benchmark.

## Qué falta y qué conviene hacer ahora

1. El perfil v2 y sus casos locales están listos y congelados. Preservarlos junto con el resultado adverso anterior; no ajustar contra el holdout.
2. Respetar la pausa y esperar reanudación explícita de la única solicitud nueva ya autorizada, aún sin consumir; no ampliar presupuesto ni reintentar automáticamente. Verificar el runner completo sin claves y revalidar saldo/precios/Stop usage.
3. Medir todos los campos y sus errores, además de latencia/tokens/costo. Mocks y referencias válidas no prueban que Nemotron mejore; una sola nota tampoco permite generalizar.
4. Verificar demo completa con Nemotron y evaluación más amplia, con métricas separadas por proveedor.
5. Preparar y, solo tras autorizaciones específicas, publicar repositorio MIT, URL, video y submission.

La debilidad inmediata es calidad semántica; además sigue faltando evidencia agronómica independiente. La integración dejó de ser una hipótesis, pero todavía no es una demo lista para jurados.

## Instrucciones para la próxima IA

Leer HANDOFF_PARA_OTRA_IA.md y cumplir su secuencia de lectura/verificación. Mantener policy.py intacto, aprobación humana, trazabilidad y separación de hechos/inferencias/recomendaciones. No sustituir datos Nemotron silenciosamente por los locales.

No inventar humanos, etiquetas ni métricas. No incorporar secretos o datos personales. Cero nuevas llamadas Nebius/Tavily, gastos, publicación, despliegue, video o submission sin permiso específico; revalidar saldo/precio/Stop usage antes de una llamada autorizada.

Continuar con mejoras locales acotadas y verificables. No prometer el premio ni confundir una extracción aceptada con calidad validada.
