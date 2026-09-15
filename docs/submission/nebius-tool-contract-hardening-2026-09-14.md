# Nemotron tool-contract hardening — 2026-09-14

> Resultado: `LOCAL_COMPATIBILITY_CANDIDATE_READY_NOT_LIVE_VALIDATED`

Este incremento es exclusivamente local. No envió solicitudes a Nebius o Tavily, no creó claves, no consumió crédito y no autoriza una nueva inferencia.

## Evidencia que motivó el cambio

Dos solicitudes reales, ejecutadas bajo autorizaciones ya agotadas, probaron conectividad con Nemotron Nano pero no produjeron una extracción aceptada. El Playground agotó su límite durante razonamiento. La llamada posterior desde el harness recibió HTTP/JSON exitoso, pero no exactamente un tool call. La versión anterior rechazó correctamente la salida, aunque no conservó suficientes metadatos saneados para demostrar la causa exacta.

La documentación oficial consultada indica que:

- Token Factory contabiliza los tokens de razonamiento dentro de `max_completion_tokens` y admite `reasoning_effort: none`;
- NVIDIA documenta que Nemotron 3 Nano razona por defecto y permite desactivarlo con `chat_template_kwargs.enable_thinking: false`;
- un esquema estricto debe cerrar objetos con `additionalProperties: false` y declarar campos requeridos.

Fuentes:

- <https://docs.tokenfactory.nebius.com/api-reference/inference/create-chat-completion>
- <https://docs.tokenfactory.nebius.com/ai-models-inference/function-calling>
- <https://docs.tokenfactory.nebius.com/ai-models-inference/json>
- <https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16>

## Cambios verificables

El commit `911d786`:

1. fija el perfil protegido de Nano en `reasoning_effort: none`;
2. envía también `extra_body.chat_template_kwargs.enable_thinking: false`;
3. conserva temperatura 0 para generación sin muestreo;
4. sustituye el esquema Pydantic con defaults por un esquema cerrado y obligatorio, con representaciones explícitas de ausencia;
5. comprueba de nuevo la forma exacta de los argumentos después de recibirlos;
6. rechaza citas asociadas a campos ausentes y cualquier nota no literal;
7. clasifica respuestas vacías, razonamiento agotado, texto libre y tool calls inválidos sin conservar el contenido;
8. mantiene una solicitud máxima por proceso y cero reintentos.

No se modificó `src/agrofield_agent/policy.py`.

## Verificación local

- suite total: 66/66 pruebas aprobadas;
- contrato Nebius: 21 pruebas aprobadas con transporte simulado;
- preflight sin red: 4.951 bytes serializados, techo de 16.384 tokens de prompt, 1.024 de salida y US$0,00122880 usando exclusivamente los precios históricos del 2026-09-14;
- salida del preflight: `network_request_sent: false`, seguida por bloqueo esperado con código 2;
- baseline local de 12 casos sin cambios: F1 0,9551, recall de omisiones 1,0000, no respaldadas 0,0000, seguridad 1,0000 y nDCG 1,0000;
- candidato local de 30 casos sin cambios: F1 0,9188, recall de omisiones 0,9714, no respaldadas 0,0050, seguridad 1,0000, nDCG 0,9877, 53 fallos y 7/17 gates;
- freeze candidato: 34/34 hashes válidos;
- `benchmark_validated: false` y cero revisiones humanas.

Estos resultados prueban lógica local, no compatibilidad real con el endpoint. No son métricas Nemotron.

## Gate de la próxima evidencia

El perfil solo puede llamarse nuevamente después de una autorización independiente con cantidad de solicitudes, cero o más reintentos explícitos, fuente de crédito, cargo personal máximo y cap total. Antes de llamar deben reconfirmarse precio, saldo promocional y `Stop usage`, crear una clave temporal y ejecutar nuevamente el preflight.

Una respuesta solo cuenta como éxito si supera todos los controles en la primera solicitud. Si falla, el reporte debe registrar el diagnóstico saneado y detenerse; nunca debe registrar la nota, la clave o el razonamiento del modelo.

## Nota histórica posterior

Este documento describía el estado inmediatamente posterior a `911d786`. Luego se
ejecutó una única solicitud autorizada por la ruta real `/api/analyze`; alcanzó la
validación local y falló por una cita no literal de `event_type`, no por conexión
upstream. No produjo una observación aceptada. El registro completo está en
`nebius-live-route-smoke-run-2026-09-14.md`. El commit local posterior `e8a926a`
agregó diagnóstico HTTP seguro y simplificó dos keywords opcionales del esquema sin
debilitar la validación client-side. No se abrió red para esa corrección.

La aceptación real llegó después de cambios adicionales de wire format y anclaje
de fuentes, en otra solicitud autorizada. El resultado pasó formato pero falló
calidad semántica; véase `nebius-source-anchor-run-2026-09-14.md`. Esta nota no
convierte los tests simulados históricos en resultados live.
