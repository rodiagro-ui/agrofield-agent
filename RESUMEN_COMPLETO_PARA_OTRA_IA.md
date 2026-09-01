# AgroField Agent — resumen completo para continuar con otra IA

> Snapshot verificable al **1 de septiembre de 2026**. Este documento distingue de forma deliberada lo construido, lo medido localmente y lo que todavía requiere validación humana o autorización.

## 1. Identidad y estado del repositorio

- **Proyecto:** AgroField Agent.
- **Competencia:** Nebius x NVIDIA Global AI Hackathon 2026.
- **Track recomendado:** Best Apps and Agents.
- **Bonus posible:** Best Use of Tavily, solamente si una prueba controlada demuestra valor real.
- **Fecha límite congelada:** 30/10/2026, 10:00 PDT / 14:00 Argentina.
- **Repositorio local:** `C:\Users\Fly Agro\Documents\Codex\2026-09-01\nebius-nvidia-agrofield-agent\outputs\agrofield-agent`.
- **Rama:** `main`.
- **Commit del MVP vertical:** `32855c4` — `Build AgroField Agent vertical MVP`.
- **Último commit funcional verificado antes de agregar este resumen:** `ebb45b9` — `Freeze blind agronomy benchmark candidate`.
- **Licencia real:** MIT.
- **Estado de Git antes de crear este documento:** limpio.

Este archivo puede quedar incluido en un commit documental posterior a `ebb45b9`. La IA que continúe debe ejecutar `git status` y `git log -1` para conocer el HEAD efectivo.

## 2. Resumen ejecutivo

AgroField Agent no es un chatbot agronómico generalista. Es un **control operativo de completitud para recorridas de soja posteriores a lluvia, granizo o viento fuerte**.

El flujo transforma una nota de campo incompleta, ingresada por texto o voz del navegador, en:

- observaciones estructuradas por lote;
- hechos enlazados con citas literales de la nota original;
- inferencias separadas de los hechos;
- omisiones críticas visibles;
- prioridades y tareas justificadas;
- una propuesta de decisión bloqueada hasta aprobación humana;
- memoria persistente y auditoría.

La diferenciación competitiva no es “hablar con una IA”, sino **probar que se observó lo suficiente antes de decidir**. Un estado rojo de “decisión bloqueada” por falta de duración del anegamiento, cantidad de puntos de muestreo o seguridad de acceso es una función central, no una limitación.

Existe un MVP vertical local funcional, un benchmark agronómico ciego **candidato** de 30 casos, un evaluador ampliado y una congelación criptográfica reproducible. No existe todavía validación agronómica humana ni una evaluación real con Nemotron.

## 3. Reglas que la siguiente IA no puede romper

Antes de modificar código, leer completos y en este orden:

1. `README.md`
2. `docs/research/official-rules-freeze-2026-09-01.md`
3. `docs/architecture.md`
4. `docs/evaluation/evaluation-spec.md`
5. `docs/submission-readiness.md`
6. `docs/research/landscape-and-idea-matrix.md`
7. `docs/video-outline.md`
8. `HANDOFF_PARA_OTRA_IA.md`

Después:

1. ejecutar `git status`;
2. ejecutar `pytest -q`;
3. reproducir el baseline local;
4. preservar cualquier cambio del usuario.

Restricciones absolutas:

- No reemplazar las decisiones de seguridad de `src/agrofield_agent/policy.py` por decisiones libres de un modelo.
- El modelo no puede rebajar severidad, ocultar omisiones, eliminar evidencia ni desactivar bloqueos.
- Separar siempre **hechos observados → inferencias → recomendaciones**.
- Nunca convertir ausencia de evidencia en evidencia de ausencia.
- Toda alerta debe apuntar a una nota, regla o fuente externa identificable.
- Toda decisión sensible requiere aprobación humana nominada y auditoría.
- No afirmar que el baseline local es un resultado Nemotron.
- No inventar revisiones agronómicas, acuerdos entre revisores ni métricas humanas.
- No incluir secretos, tokens, datos personales, nombres reales, establecimientos reales ni coordenadas exactas.
- No contactar personas reales ni manejar datos reales sin autorización expresa.
- No hacer público el repositorio, desplegar, consumir créditos, ejecutar llamadas a Nebius/Tavily, publicar video ni registrar la submission sin autorización expresa.
- Antes de una llamada potencialmente paga, solicitar autorización y un límite de gasto concreto.

## 4. Requisitos oficiales congelados

La investigación de bases está documentada con fuentes en `docs/research/official-rules-freeze-2026-09-01.md`. El estado congelado indica:

- Argentina es elegible.
- La aplicación final debe ejecutarse en Nebius Token Factory o Nebius AI Cloud.
- Debe usar al menos un modelo open source de NVIDIA/Nemotron.
- La entrega final requiere URL pública funcional.
- Requiere repositorio público, licencia open source y README reproducible.
- Requiere video público de menos de tres minutos.
- La entrega debe estar en inglés o incluir traducción al inglés.
- Si se reutiliza código anterior, hay que documentar cambios significativos posteriores al 26/08/2026.
- Tavily es opcional; su bonus no justifica una integración decorativa.

Nada de lo anterior que implique publicación, despliegue, registro o gasto fue ejecutado.

## 5. Investigación y decisión de producto realizadas

Se estudió el patrón de ganadores recientes y productos agronómicos comparables. La conclusión fue que ya existe mucha oferta de asistentes por voz, diagnóstico, tableros de scouting y generación automática de tareas. Competir como “agronomista digital” sería común, difícil de evaluar y riesgoso.

La matriz de ideas comparó seis direcciones. La opción ganadora fue **post-event soybean scouting completeness gate**, con puntuación ponderada 4,75/5, por su impacto, demostrabilidad, diferenciación y facilidad de evaluación.

El flujo de campo conceptual quedó documentado como hipótesis, no como investigación humana completada:

1. priorizar lotes antes de salir;
2. confirmar lote, cultivo, estado, fecha y seguridad;
3. recorrer una trayectoria deliberada con varios puntos;
4. medir daño, superficie, agua, plantas y señales relevantes;
5. convertir la nota en evidencia estructurada y preguntas mínimas;
6. requerir decisión humana;
7. crear tareas y conservar historial.

## 6. Arquitectura construida

1. **Interfaz web móvil:** texto y dictado mediante reconocimiento de voz del navegador.
2. **FastAPI:** API y aplicación web.
3. **SQLite:** lotes, recorridas, observaciones, tareas, decisiones y auditoría.
4. **Extractor local determinista:** desarrollo y regresión sin red ni costo.
5. **Adaptador Nebius/Nemotron:** preparado por variables de entorno, todavía no ejecutado contra el servicio real.
6. **Motor de políticas deterministas:** propietario de los campos críticos, severidad, evidencia y bloqueos.
7. **Aprobación humana:** aprobar, rechazar o diferir tareas con identidad del revisor.
8. **Tavily opcional y restringido:** pensado solo para alertas oficiales recientes, con allowlist, URL y fecha; no puede probar presencia en un lote ni autorizar tratamiento.

Límite de confianza fundamental:

```text
nota/voz + clima + historial
             ↓
   extracción estructurada
             ↓
 reglas deterministas + evidencia
             ↓
 tareas propuestas y decisión bloqueada
             ↓
     aprobación humana auditada
```

## 7. Funcionalidad ya implementada

- Alta y consulta de lotes.
- Creación de recorridas.
- Entrada de observaciones por texto o voz del navegador.
- Extracción estructurada con evidencia literal.
- Detección de información crítica faltante.
- Alertas justificadas.
- Priorización de lotes/tareas.
- Memoria histórica por lote.
- Propuestas de decisión no autónomas.
- Aprobación/rechazo humano y registro de auditoría.
- Manejo local de fallos y proveedor determinista reproducible.
- Adaptador configurable para Nebius Token Factory/Nemotron.
- Conector Tavily desactivado por defecto y limitado por diseño.
- Fixtures sintéticos, evaluador y pruebas automáticas.
- README, arquitectura, especificación de evaluación, checklist de entrega y guion de video.
- Licencia MIT, `.env.example`, Dockerfile y documentación de cambios significativos.

`policy.py` fue comparado contra `32855c4` y permanece sin cambios.

## 8. Benchmark Agronómico Ciego v1: trabajo completado

Se agregó `benchmark/agronomy_blind_v1/` con:

- consentimiento y política de privacidad/anonimización;
- guía de entrevista neutral para 3–5 asesores/productores;
- instrucciones de revisión ciega;
- rúbrica campo por campo;
- clasificación de tareas: apropiada, prematura, insegura o no evaluable;
- plantillas para entrevista, anotación, revisión de salida y adjudicación;
- 30 casos sintéticos candidatos;
- división fija de 20 casos de desarrollo y 10 de holdout;
- 10 IDs fijados para doble revisión;
- dataset card y directorios para revisiones/reportes;
- generación de paquetes ciegos que excluyen proveedor, modelo, split, telemetría, coordenadas y referencia;
- manifiesto de congelación con hashes SHA-256.

Composición de los 30 candidatos:

- 12 casos enlazados con los fixtures heredados;
- 18 casos adversariales nuevos;
- 30/30 marcados `synthetic_no_real_data`;
- coordenadas de demo reemplazadas por el sentinel no geográfico `0.0,0.0`;
- 0/30 revisiones primarias humanas;
- 0/10 revisiones dobles humanas.

La congelación actual es **candidate-only**. Verifica que no se altere silenciosamente el paquete previo a revisión, pero no equivale a un benchmark humano final.

## 9. Extensión del evaluador

El evaluador ahora calcula o prepara:

- precisión, recall y F1 micro de extracción;
- recall de omisiones críticas;
- tasa de afirmaciones no respaldadas;
- cobertura de citas de evidencia;
- seguridad de bloqueo de decisiones;
- integridad de aprobación humana;
- nDCG de priorización;
- task precision basada exclusivamente en etiquetas humanas;
- matriz de errores E1–E8;
- listado de fallos adversos por caso;
- completitud de revisión primaria y doble;
- desacuerdo bruto y Cohen’s kappa para variables nominales;
- acuerdo bruto para variables numéricas;
- validación de requisitos de benchmark;
- opción `--require-validated` para impedir presentar un resultado no validado como final.

También se agregó `src/agrofield_agent/freeze.py` para verificar el manifiesto congelado.

## 10. Commits realizados

| Commit | Resultado |
|---|---|
| `32855c4` | MVP vertical funcional. |
| `29bcaaa` | Primer handoff para otra IA. |
| `f148074` | Corrección de rutas documentales y licencia MIT. |
| `42bd611` | Protocolo y plantillas del benchmark agronómico ciego. |
| `4019e60` | Conjunto candidato de 30 casos, split y casos de doble revisión. |
| `16a22ae` | Evaluador ampliado, revisión humana, E1–E8 y acuerdo. |
| `ebb45b9` | Freeze reproducible del benchmark candidato. |

Entre `32855c4` y `ebb45b9` se agregaron aproximadamente 2.887 líneas y 29 archivos modificados, principalmente benchmark, evaluación, privacidad, pruebas y documentación.

## 11. Verificación reproducida al crear este resumen

### Pruebas

- **16/16 pruebas pasaron**.
- Advertencia no bloqueante: `StarletteDeprecationWarning` por la combinación actual de FastAPI/Starlette TestClient y `httpx`.

### Baseline heredado: local y determinista

Comando: `python -m agrofield_agent.evaluate fixtures/eval_cases.jsonl`

| Métrica | Resultado |
|---|---:|
| Casos | 12 |
| Precisión de extracción | 0,9884 |
| Recall de extracción | 0,9239 |
| F1 micro | 0,9551 |
| Recall de omisiones críticas | 1,0000 |
| Afirmaciones no respaldadas | 0,0000 |
| Cobertura de citas | 1,0000 |
| Seguridad de bloqueo | 1,0000 |
| Integridad de aprobación | 1,0000 |
| nDCG | 1,0000 |
| Latencia p50 local de esta ejecución | 0,061 ms |
| Costo estimado | US$0 |
| Proveedor | `local/deterministic-es-v0.1` |

Advertencia: es una regresión sobre 12 fixtures sintéticos y potencialmente circulares. No es un resultado Nemotron, no fue validado por agrónomos y no demuestra impacto de campo.

### Benchmark ciego candidato: local y determinista

Comando: `python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl`

| Métrica | Resultado |
|---|---:|
| Casos | 30 |
| Precisión de extracción | 0,9851 |
| Recall de extracción | 0,8609 |
| F1 micro | 0,9188 |
| Recall de omisiones críticas | 0,9714 |
| Afirmaciones no respaldadas | 0,0050 |
| Cobertura de citas | 1,0000 |
| Seguridad de bloqueo | 1,0000 |
| Integridad de aprobación | 1,0000 |
| nDCG | 0,9877 |
| Task precision humana | no disponible |
| Fallos adversos | 53 |
| Estado | `benchmark_validated: false` |

Desglose automático dominante: 31 errores E5 (omisión de un hecho esperado) y 17 E6 (orden de prioridad distinto de la referencia candidata). El recall crítico 0,9714 queda por debajo del umbral de liberación 0,98.

Estas etiquetas de referencia siguen siendo candidatas sintéticas. Los errores sirven para orientar la revisión, no para ajustar el holdout ni para proclamar calidad agronómica.

### Integridad del freeze

- 18 archivos declarados.
- 18 hashes coincidentes.
- 0 ausentes.
- 0 modificados.
- Resultado: `valid: true`.

## 12. Estado honesto del incremento “Benchmark Agronómico Ciego v1”

La **infraestructura y el conjunto candidato** están construidos. El incremento no puede considerarse terminado bajo su definición original porque faltan acciones humanas externas:

- entrevistar 3–5 asesores/productores;
- obtener al menos una revisión agronómica de cada uno de los 30 casos;
- obtener una segunda anotación independiente de los 10 casos fijados;
- calcular desacuerdo real y Cohen’s kappa;
- adjudicar desacuerdos sin borrar el historial;
- revisar y clasificar todas las tareas propuestas;
- alcanzar task precision ≥0,90;
- congelar dataset, rúbrica y umbrales finales después de la revisión.

No se contactó a nadie porque eso requiere autorización expresa. **La siguiente IA no debe completar esos casilleros con etiquetas simuladas ni tratar una revisión generada por IA como revisión agronómica humana.**

## 13. Debilidad crítica que impide ganar hoy

La carencia principal es una **cadena de evidencia externa y humana defendible**. El producto y su aparato de evaluación son prometedores, pero todos los casos y referencias actuales son sintéticos. Por tanto:

- no hay prueba de que el problema sea frecuente y costoso para asesores argentinos;
- no hay prueba independiente de que los campos críticos y tareas sean agronómicamente correctos;
- no hay acuerdo entre revisores;
- no hay comparación real local vs Nemotron;
- no hay costo ni latencia medidos en Nebius;
- no existe una demostración pública ejecutándose en el runtime obligatorio.

Optimizar más código antes de validar con humanos tiene menor retorno y riesgo de sobreajuste a etiquetas circulares.

## 14. Acciones externas y costos: estado exacto

- Llamadas reales a Nebius: **0**.
- Llamadas reales a Tavily: **0**.
- Costo Nebius/Tavily: **US$0**.
- Datos personales recolectados: **0**.
- Personas reales contactadas: **0**.
- Repositorio público: **no**.
- URL pública: **no**.
- Despliegue: **no**.
- Video grabado/publicado: **no**.
- Submission registrada: **no**.

## 15. Próxima secuencia de mayor impacto

### Paso 1 — autorización y validación humana

Solicitar autorización para contactar o invitar a 3–5 asesores/productores y para que uno o más agrónomos revisen el paquete anonimizado. Definir antes:

- canal de contacto;
- texto de consentimiento;
- prohibición de nombres, coordenadas y establecimientos;
- dónde se guardarán las respuestas;
- responsables de revisión primaria, doble y adjudicación.

### Paso 2 — congelar el benchmark humano final

- Incorporar 30 revisiones primarias.
- Incorporar las 10 dobles independientes.
- Calcular acuerdo/desacuerdo.
- Adjudicar y versionar, sin borrar etiquetas previas.
- Ejecutar `--require-validated`.
- No tocar el holdout después de abrir sus resultados.

### Paso 3 — evaluación controlada con Nemotron

Solo con autorización y límite de gasto:

- confirmar modelo NVIDIA/Nemotron elegible y precio vigente;
- probar conectividad con un smoke test mínimo;
- correr el mismo benchmark congelado local vs Nemotron;
- registrar modelo exacto, configuración, latencia, tokens, fallos y costo;
- hacer análisis pareado por caso, no solo promedios.

### Paso 4 — decisión Tavily basada en datos

Realizar una ablación `sin Tavily` vs `con Tavily` únicamente sobre alertas oficiales recientes. Exigir mejora medible de priorización o cobertura, trazabilidad de URL/fecha y costo razonable. Si no mejora, no integrarlo.

### Paso 5 — producto y entrega

- robustecer UX móvil, fallos, privacidad, autenticación y separación entre organizaciones;
- preparar demo de 2:35–2:50;
- mostrar nota incompleta, omisión, evidencia, prioridad y aprobación humana;
- mostrar métricas Nemotron reales, no las locales;
- preparar README, formulario, video y despliegue;
- publicar y enviar solamente con autorización final.

## 16. Comandos de reproducción

En PowerShell:

```powershell
cd "C:\Users\Fly Agro\Documents\Codex\2026-09-01\nebius-nvidia-agrofield-agent\outputs\agrofield-agent"

git status --short --branch
git log --oneline -8

.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m agrofield_agent.evaluate fixtures/eval_cases.jsonl
.\.venv\Scripts\python.exe -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl
.\.venv\Scripts\python.exe -m agrofield_agent.freeze benchmark/agronomy_blind_v1/freeze/manifest.json --root .
```

Para iniciar la aplicación local:

```powershell
.\.venv\Scripts\python.exe -m agrofield_agent
```

No copiar credenciales al repositorio. Usar únicamente las variables documentadas en `.env.example` y mantenerlas fuera de Git.

## 17. Mapa mínimo de archivos

- `README.md`: instalación, ejecución y alcance.
- `HANDOFF_PARA_OTRA_IA.md`: handoff anterior más narrativo.
- `src/agrofield_agent/main.py`: aplicación y endpoints.
- `src/agrofield_agent/policy.py`: controles deterministas inviolables.
- `src/agrofield_agent/evaluate.py`: evaluador.
- `src/agrofield_agent/benchmarking.py`: revisión humana, acuerdo y paquetes ciegos.
- `src/agrofield_agent/freeze.py`: verificación de integridad.
- `src/agrofield_agent/providers/`: proveedor local y adaptador Nebius/Nemotron.
- `src/agrofield_agent/database.py`: persistencia SQLite.
- `src/agrofield_agent/static/`: interfaz web móvil.
- `fixtures/eval_cases.jsonl`: regresión sintética heredada de 12 casos.
- `benchmark/agronomy_blind_v1/`: benchmark candidato completo.
- `benchmark/agronomy_blind_v1/data/cases.jsonl`: 30 candidatos.
- `benchmark/agronomy_blind_v1/freeze/manifest.json`: hashes del freeze candidato.
- `benchmark/agronomy_blind_v1/reports/local-candidate-2026-09-01.json`: reporte local candidato.
- `docs/evaluation/evaluation-spec.md`: métricas, errores y umbrales.
- `docs/submission-readiness.md`: checklist y gates de publicación.
- `docs/video-outline.md`: guion preliminar.
- `tests/`: pruebas automáticas.

## 18. Prompt listo para pegar a otra IA

```text
Continúa AgroField Agent desde este repositorio. Lee primero, completos y en este orden: README.md; docs/research/official-rules-freeze-2026-09-01.md; docs/architecture.md; docs/evaluation/evaluation-spec.md; docs/submission-readiness.md; docs/research/landscape-and-idea-matrix.md; docs/video-outline.md; HANDOFF_PARA_OTRA_IA.md; y RESUMEN_COMPLETO_PARA_OTRA_IA.md. Luego ejecuta git status, pytest -q, el baseline de fixtures/eval_cases.jsonl, el benchmark candidato benchmark/agronomy_blind_v1/data/cases.jsonl y la verificación del freeze.

No sustituyas policy.py ni permitas que un modelo desactive controles deterministas. Separa hechos, inferencias y recomendaciones; exige evidencia y aprobación humana. Distingue siempre local/deterministic-es-v0.1 de cualquier resultado Nemotron. El benchmark actual tiene 30 casos sintéticos pero 0 revisiones humanas y benchmark_validated=false: no inventes etiquetas ni declares validación.

No contactes personas, manejes datos reales, publiques, despliegues, consumas Nebius/Tavily, generes costos, subas video ni registres la submission sin autorización humana expresa. Antes de servicios pagos solicita autorización y límite de gasto.

La prioridad es cerrar la cadena de evidencia: validación con 3–5 usuarios, 30 revisiones agronómicas primarias, 10 dobles y adjudicación; luego congelar el benchmark humano y recién entonces comparar Nemotron contra el baseline local. Reporta hechos verificables, la debilidad más crítica y el siguiente incremento de mayor ROI.
```

## 19. Definición de victoria

La demo final debe demostrar en menos de tres minutos:

1. una nota de campo incompleta;
2. su transformación en una recorrida estructurada;
3. una omisión crítica detectada;
4. una alerta con evidencia visible;
5. una prioridad justificable;
6. una decisión bloqueada hasta aprobación humana;
7. ejecución real con NVIDIA/Nemotron en Nebius;
8. evaluación reproducible, costo y latencia reales;
9. URL pública, repositorio MIT reproducible y video público válidos.

Hoy están resueltos los puntos 1–6 en el MVP local y la infraestructura para medirlos. Faltan validación humana, ejecución Nemotron real y todos los actos públicos de entrega.
