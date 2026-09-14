# Nebius live `/api/analyze` smoke — 2026-09-14

> Resultado: `LIVE_ROUTE_ONE_UPSTREAM_REQUEST_FAILED_BEFORE_CONTRACT`

Este registro documenta un intento real y controlado a través de la ruta de la
aplicación. No es una extracción Nemotron aceptada, no es una evaluación y no
demuestra que el modelo haya iniciado o completado inferencia.

## Autorización y controles previos

El usuario autorizó exactamente:

- una solicitud API de AgroField, sin reintentos;
- el modelo `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`;
- hasta US$0,01 de crédito promocional y US$0 de cargo personal;
- crear y revocar una clave temporal solo para esta prueba;
- detenerse si faltaba crédito o aparecía un cobro.

Antes de ejecutar, la interfaz autenticada de Token Factory mostró:

- precio de Nano: US$0,06 por millón de tokens de entrada y US$0,24 por millón
  de salida;
- trial: US$1,00 disponible y 29 días restantes;
- saldo de cuenta: US$0,00;
- fallback post-trial: `Usage stops after the trial`.

El preflight conservador del perfil calculó US$0,00122880, por debajo del cap.
La clave temporal se inyectó en el entorno del proceso servidor y no se escribió
en `.env`, archivos, logs de la aplicación ni Git. Su valor sí quedó visible en
la sesión privada de automatización al copiarlo desde la interfaz; por eso la
revocación posterior era obligatoria. Tavily permaneció desactivado.

## Ejecución

Se inició el FastAPI real de AgroField en `127.0.0.1:8000` con:

- `AGROFIELD_PROVIDER=nebius`;
- Nano, 1.024 tokens máximos de salida y presupuesto conservador de 16.384
  tokens de prompt;
- `reasoning_effort: none` y pensamiento desactivado;
- herramienta obligatoria, una solicitud máxima por proceso y cero retries;
- SQLite temporal y una nota exclusivamente sintética;
- `use_tavily: false`.

El cliente local envió un único `POST /api/analyze`. La ruta respondió HTTP 503:

```json
{"detail":"Nebius request failed; no automatic retry was attempted"}
```

No hubo segundo intento. La versión ejecutada saneaba toda excepción
`httpx.HTTPError` con el mismo mensaje y no preservaba el estado HTTP upstream
ni un request ID. Por eso solo puede afirmarse que la ruta abrió el intento a
Nebius y encontró un fallo HTTP o de transporte antes de validar el contrato.
No puede determinarse si el endpoint rechazó la solicitud, si falló el
transporte o si el modelo llegó a ejecutarse.

No se obtuvo tool call, `ObservationDraft`, texto del modelo, uso de tokens,
costo estimado desde telemetría ni salida que pueda evaluarse. Este intento no
es evidencia de calidad Nemotron ni satisface el requisito de una aplicación
funcional ejecutada con Nemotron.

## Limpieza y observaciones posteriores

Después del único intento:

- se cerró el proceso servidor y se comprobó que el puerto 8000 ya no escuchaba;
- se eliminó la base SQLite temporal;
- se limpió el portapapeles;
- se revocó la clave temporal con confirmación del usuario;
- la interfaz mostró vacía la lista de API keys;
- la página de uso mostró inmediatamente `No usage`, trial US$1,00 y saldo
  US$0,00.

La consulta de uso fue inmediata y puede sufrir demora o redondeo. Demuestra
que no había cargo visible en ese momento; no demuestra costo promocional
contabilizado igual a cero.

## Corrección local posterior

Sin abrir red, el commit `e8a926a`:

1. conserva estado HTTP, request ID seguro y latencia ante futuros fallos
   upstream, sin guardar cuerpo, nota o clave;
2. separa fallos HTTP de transporte;
3. elimina `minLength` y `uniqueItems` del JSON Schema enviado para reducir
   incompatibilidades opcionales, pero conserva la validación de duplicados y
   contenido del lado cliente;
4. mantiene exactamente una solicitud por proceso, cero reintentos y todos los
   controles de evidencia.

El commit `9cf6dd3` agregó una prueba explícita de la unicidad client-side.

La causa del fallo live sigue desconocida. La simplificación del esquema es una
medida de compatibilidad informada, no una explicación probada. La corrección
posterior tiene pruebas locales con transporte simulado y no fue llamada contra
Nebius.

## Estado de autorización

La autorización de esta solicitud fue consumida. No queda autorización para
crear otra clave, repetir la llamada, ejecutar una evaluación Nemotron, llamar
a Tavily, desplegar, publicar, subir video o enviar la submission.
