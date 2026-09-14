# Nemotron raw wire-format correction — 2026-09-14

> Resultado: `LOCAL_WIRE_FORMAT_CANDIDATE_READY_NOT_LIVE_VALIDATED`

Este incremento es exclusivamente local. No creó una clave, no abrió red y no
consumió crédito.

## Hallazgo

AgroField usa `httpx` y serializa el JSON HTTP directamente. El perfil anterior
enviaba:

```json
{"extra_body":{"chat_template_kwargs":{"enable_thinking":false}}}
```

Eso confundía una opción del SDK OpenAI con el cuerpo raw. La documentación de
Token Factory muestra esta semántica: su ejemplo Python pasa `guided_json`
dentro del argumento SDK `extra_body`, mientras el cURL equivalente envía
`guided_json` directamente en la raíz del JSON. La guía del modelo NVIDIA hace
la misma distinción para desactivar pensamiento: `extra_body` en el cliente
OpenAI, pero `chat_template_kwargs` en la raíz al usar cURL.

Fuentes consultadas el 2026-09-14:

- <https://docs.tokenfactory.nebius.com/api-reference/examples/text-generation>
- <https://docs.tokenfactory.nebius.com/ai-models-inference/function-calling>
- <https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8>

El commit `e0f0ad2` ahora envía:

```json
{"chat_template_kwargs":{"enable_thinking":false}}
```

El test de transporte simulado comprueba tanto la presencia del parámetro en la
raíz como la ausencia de la clave `extra_body`.

## Alcance probatorio

Este hallazgo explica de forma coherente la diferencia entre el primer request
del harness —que no incluía `extra_body` y obtuvo HTTP/JSON 2xx— y el intento
posterior por `/api/analyze`, que falló upstream antes de una salida observable.
No confirma causalidad: la versión live no conservó el estado ni el cuerpo
upstream. Por lo tanto, `extra_body` mal serializado es la hipótesis principal,
no una causa demostrada.

## Verificación local

- suite: 68/68 pruebas aprobadas;
- contrato Nebius simulado: 23 pruebas;
- preflight sin red: 4.889 bytes serializados;
- techo histórico: US$0,00122880;
- resultado esperado: `network_request_sent: false` y salida 2 por falta de
  confirmación live;
- `policy.py`: sin cambios;
- Tavily: no llamado.

La única validación concluyente sería una nueva solicitud con estado/request ID
saneados. Requiere una autorización independiente, cap explícito, verificación
de precio/crédito/`Stop usage` y una clave temporal nueva. Este documento no la
autoriza.
