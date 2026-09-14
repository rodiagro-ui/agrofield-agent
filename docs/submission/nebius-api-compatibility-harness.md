# Nebius API compatibility harness

> Estado: endurecido localmente después de dos ejecuciones reales adversas desde el repositorio. Hay 23 pruebas con transporte simulado. El contrato corregido todavía no fue validado con una salida real y este documento no autoriza otra llamada.

## Propósito

`python -m agrofield_agent.nebius_smoke` convierte una eventual autorización limitada en una sola solicitud controlada. El mismo contrato está conectado a `create_app()` cuando `AGROFIELD_PROVIDER=nebius`. El harness existe porque el smoke del Playground del 2026-09-14 agotó 256 tokens en razonamiento y porque la primera llamada desde el repositorio respondió sin el tool call obligatorio. Una ejecución posterior por `/api/analyze` falló upstream antes de que pudiera observarse una salida del modelo.

El contrato sigue la API oficial de Token Factory:

- endpoint compartido `https://api.tokenfactory.nebius.com/v1/chat/completions`;
- function calling con `tool_choice` explícito;
- `max_completion_tokens`, que incluye salida visible y tokens de razonamiento;
- `reasoning_effort: none` y `extra_body.chat_template_kwargs.enable_thinking: false` para desactivar razonamiento por las dos vías documentadas;
- temperatura 0, coherente con generación greedy sin razonamiento, `n: 1`, sin streaming y `store: false`;
- esquema estricto cerrado: todos los campos son obligatorios, la ausencia se representa con `null`, `unknown`, listas vacías o citas vacías y no se admiten propiedades adicionales.

Fuentes consultadas el 2026-09-14:

- <https://docs.tokenfactory.nebius.com/api-reference/inference/create-chat-completion>
- <https://docs.tokenfactory.nebius.com/ai-models-inference/function-calling>
- <https://docs.tokenfactory.nebius.com/ai-models-inference/json>
- <https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16>

## Garantías locales

Antes de abrir red:

1. exige un host HTTPS de Token Factory terminado en `/v1`;
2. serializa la solicitud y comprueba un presupuesto conservador de prompt;
3. calcula un techo de costo con precios introducidos por el operador;
4. bloquea si el techo supera `--max-cost-usd`;
5. no acepta la clave por argumento: solo lee `NEBIUS_API_KEY` del entorno;
6. exige la frase exacta `RUN_ONE_NEBIUS_REQUEST` en cada ejecución live.

Durante y después de la llamada:

- realiza un único `POST`, sin retry automático;
- la aplicación admite como máximo una solicitud Nebius por proceso, incluso si la primera falla;
- fuerza exactamente un tool call `record_field_observation`;
- rechaza respuesta vacía, texto libre, JSON inválido, herramienta equivocada o múltiples tool calls;
- vuelve a comprobar que los argumentos contienen exactamente el esquema cerrado, aunque el servidor ignore `strict`;
- valida `ObservationDraft`, exige citas literales por cada hecho no nulo, citas vacías para campos ausentes y notas estrictamente literales;
- exige `prompt_tokens`, `completion_tokens` y request ID;
- calcula costo estimado desde el uso reportado;
- ante un fallo conserva solo diagnóstico saneado: forma de respuesta, conteos, presencia y longitud de contenido/razonamiento, uso, latencia y request ID; nunca el texto generado, la clave ni la nota cruda.
- ante un HTTP no exitoso conserva solo estado, request ID de caracteres seguros y latencia; ante transporte fallido conserva solo latencia. Nunca conserva el cuerpo upstream.

Los precios deben volver a verificarse en la interfaz autenticada inmediatamente antes de una ejecución. Los valores observados el 2026-09-14 para `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` fueron US$0,06 por millón de tokens de entrada y US$0,24 por millón de salida; no se asume que sigan vigentes.

## Preflight sin red

Este comando no incluye confirmación live; imprime el preflight y termina bloqueado con código 2, sin leer una clave ni enviar una solicitud:

```powershell
.\.venv\Scripts\python.exe -m agrofield_agent.nebius_smoke `
  --note-file fixtures/nebius_smoke_note.txt `
  --input-price-per-million 0.06 `
  --output-price-per-million 0.24 `
  --max-cost-usd 0.01
```

## Primera ejecución real

Una autorización separada permitió exactamente una llamada, cero reintentos, hasta
US$0,01 de crédito promocional y US$0 personal. El preflight calculó un techo de
US$0,00122880. La API respondió, pero la salida no contenía exactamente un tool call;
el harness la rechazó y no reintentó. La clave temporal fue revocada y la lista de
claves quedó vacía. Véase `nebius-api-smoke-run-2026-09-14.md`.

El perfil de esa ejecución histórica usó `reasoning_effort: low` y el esquema Pydantic directo. Después del fallo, el commit `911d786` introdujo el perfil sin razonamiento, el esquema cerrado y los diagnósticos saneados. La causa exacta de la respuesta sin tool call no puede probarse porque la primera versión no preservó esos metadatos; agotamiento en razonamiento y compatibilidad del esquema son hipótesis, no hechos.

## Ejecución por la ruta real

Una tercera autorización separada permitió una única solicitud por `/api/analyze`,
cero reintentos, hasta US$0,01 promocional y US$0 personal. La ruta local respondió
HTTP 503 con un fallo upstream saneado. La versión ejecutada no distinguía HTTP de
transporte ni preservaba estado/request ID, de modo que no se puede probar que el
modelo haya iniciado inferencia. No hubo tool call ni salida evaluable. La clave fue
revocada y la lista quedó vacía. Véase
`nebius-live-route-smoke-run-2026-09-14.md`.

Después de ese intento, `e8a926a` agregó metadatos HTTP seguros y eliminó del esquema
enviado `minLength` y `uniqueItems`, manteniendo la validación equivalente del lado
cliente. La causa live sigue sin conocerse y el nuevo perfil solo está verificado
localmente.

## Preflight actual, sin red

Con la nota sintética congelada y los precios históricos —solo para reproducir el cálculo— el perfil endurecido serializa 4.904 bytes y mantiene el mismo techo conservador de US$0,00122880. El comando termina con código 2 por falta deliberada de confirmación live y reporta `network_request_sent: false`.

## Gate para una futura llamada

No volver a ejecutar. Solo después de una nueva autorización explícita que indique proveedor, cantidad máxima de llamadas, crédito permitido, cargo personal máximo y cap total:

1. verificar precios y fallback de facturación en Token Factory;
2. crear una clave temporal y cargarla privadamente en `NEBIUS_API_KEY`;
3. repetir el preflight con los precios vigentes y guardar solo su salida saneada;
4. añadir `--confirm-live RUN_ONE_NEBIUS_REQUEST` una sola vez;
5. revocar la clave después de capturar el reporte saneado.

Para probar el recorrido mediante la aplicación en vez del CLI, configurar además `AGROFIELD_PROVIDER=nebius` y `AGROFIELD_NEBIUS_LIVE_CONFIRMATION=RUN_ONE_NEBIUS_REQUEST`. El arranque se bloquea si faltan clave, precios o cap. Al terminar, cerrar el proceso, limpiar las variables sensibles y revocar la clave.

La aceptación requiere, en la misma única respuesta: HTTP/JSON válido, exactamente un tool call, argumentos cerrados y válidos, citas literales, telemetría completa y costo estimado dentro del cap. Cualquier otra salida es fallo y no se reintenta.

Las autorizaciones del Playground, del primer harness y de la ruta `/api/analyze` están agotadas. El endurecimiento local no amplía esos permisos.
