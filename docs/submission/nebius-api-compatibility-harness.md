# Nebius API compatibility harness

> Estado: implementado, cubierto con transporte simulado y ejecutado una vez contra la API real el 2026-09-14. La conectividad pasó, pero Nemotron no devolvió exactamente un tool call y el contrato lo rechazó. No constituye una evaluación Nemotron ni autorización para repetir la llamada.

## Propósito

`python -m agrofield_agent.nebius_smoke` convierte la próxima autorización limitada en una sola solicitud controlada. El mismo contrato está conectado a `create_app()` cuando `AGROFIELD_PROVIDER=nebius`. El harness existe porque el smoke del Playground del 2026-09-14 probó conectividad, pero agotó 256 tokens en razonamiento y devolvió un mensaje final vacío.

El contrato sigue la API oficial de Token Factory:

- endpoint compartido `https://api.tokenfactory.nebius.com/v1/chat/completions`;
- function calling con `tool_choice` explícito;
- `max_completion_tokens`, que incluye salida visible y tokens de razonamiento;
- `reasoning_effort: low`, temperatura 0, `n: 1`, sin streaming y `store: false`.

Fuentes consultadas el 2026-09-14:

- <https://docs.tokenfactory.nebius.com/api-reference/inference/create-chat-completion>
- <https://docs.tokenfactory.nebius.com/ai-models-inference/function-calling>

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
- valida `ObservationDraft` y exige citas literales por cada hecho no nulo;
- exige `prompt_tokens`, `completion_tokens` y request ID;
- calcula costo estimado desde el uso reportado;
- nunca imprime la clave ni la nota cruda en el resultado.

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

## Gate para una futura llamada

No volver a ejecutar. Solo después de una nueva autorización explícita que indique proveedor, cantidad máxima de llamadas, crédito permitido, cargo personal máximo y cap total:

1. verificar precios y fallback de facturación en Token Factory;
2. crear una clave temporal y cargarla privadamente en `NEBIUS_API_KEY`;
3. repetir el preflight con los precios vigentes;
4. añadir `--confirm-live RUN_ONE_NEBIUS_REQUEST` una sola vez;
5. revocar la clave después de capturar el reporte saneado.

Para probar el recorrido mediante la aplicación en vez del CLI, configurar además `AGROFIELD_PROVIDER=nebius` y `AGROFIELD_NEBIUS_LIVE_CONFIRMATION=RUN_ONE_NEBIUS_REQUEST`. El arranque se bloquea si faltan clave, precios o cap. Al terminar, cerrar el proceso, limpiar las variables sensibles y revocar la clave.

Las autorizaciones del Playground y de la primera ejecución del harness están agotadas. El harness no amplía esos permisos.
