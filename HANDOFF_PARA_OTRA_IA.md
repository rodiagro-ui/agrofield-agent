# AgroField Agent — resumen y handoff para otra IA

**Estado al 1 de septiembre de 2026**  
**Repositorio local:** `C:\Users\Fly Agro\Documents\Codex\2026-09-01\nebius-nvidia-agrofield-agent\outputs\agrofield-agent`  
**Rama:** `main`  
**Commit base:** `32855c4` — `Build AgroField Agent vertical MVP`

## Resumen ejecutivo

AgroField Agent es un proyecto independiente para competir en **Nebius x NVIDIA Global AI Hackathon 2026**. No busca ser un chatbot agronómico genérico: el MVP implementa un flujo operativo estrecho para recorridas de soja posteriores a un evento meteorológico.

El sistema convierte observaciones de campo en español, ingresadas por texto o dictadas desde el navegador, en:

- una recorrida estructurada por lote;
- alertas con evidencia trazable;
- controles de información crítica faltante;
- tareas priorizadas;
- una propuesta de decisión que requiere aprobación humana;
- un registro auditable de cada cambio y aprobación.

Ya existe un **MVP vertical funcional y probado localmente**, construido con FastAPI, SQLite y una interfaz web móvil. Incluye un extractor determinista para desarrollo sin costo, un adaptador preparado para Nemotron mediante Nebius Token Factory, reglas de seguridad deterministas, memoria por lote, aprobación humana y una integración Tavily opcional y restringida.

El proyecto **todavía no fue publicado, desplegado ni enviado al hackathon**. Tampoco se ejecutaron llamadas pagas a Nebius o Tavily. Esas acciones requieren autorización expresa del usuario.

## Objetivo del hackathon y restricciones congeladas

- Fecha límite: **30/10/2026 a las 10:00 PDT**, equivalente a **14:00 en Argentina**.
- Argentina es elegible.
- Premios generales informados: **US$20.000, US$10.000 y US$6.000**.
- Bonus Best Use of Tavily: **US$3.000**.
- Track recomendado: **Best Apps and Agents**.
- La aplicación final debe ejecutarse en **Nebius Token Factory o Nebius AI Cloud**.
- Debe usar al menos un modelo open source de **NVIDIA/Nemotron**.
- La entrega requiere URL pública funcional, repositorio público con licencia open source y README reproducible, y video público de menos de tres minutos.
- Tavily debe integrarse en runtime solamente si aporta valor real; no debe agregarse de forma decorativa.
- Si se reutiliza código previo, deben documentarse cambios significativos realizados después del 26/08/2026.
- No publicar, desplegar con costos, hacer público el repositorio ni registrar una submission sin autorización expresa del usuario.

La evidencia y las fuentes oficiales congeladas están documentadas en `docs/official-rules-freeze.md`.

## Decisión de producto

### Caso de uso seleccionado

**Control de completitud y priorización de una recorrida de soja posterior a lluvia, granizo o viento fuerte.**

El asesor recorre un lote y dicta observaciones. El agente estructura los hallazgos, identifica datos críticos que no fueron observados, separa evidencia de inferencias, crea tareas y bloquea decisiones sensibles hasta que una persona revise y apruebe.

### Por qué se eligió

La investigación inicial mostró que “asistente agronómico por voz” o “chatbot que recomienda” es una idea común y difícil de diferenciar. El flujo elegido es más demostrable porque permite medir:

- exactitud de extracción;
- omisiones críticas detectadas;
- afirmaciones sin respaldo;
- seguridad de los bloqueos de decisión;
- calidad del orden de prioridades;
- latencia y costo.

La comparación de alternativas está en `docs/idea-landscape-matrix.md`.

## Arquitectura recomendada e implementada

1. **Entrada móvil:** texto o dictado mediante la API de reconocimiento de voz disponible en el navegador.
2. **API FastAPI:** recibe notas, estado meteorológico y antecedentes del lote.
3. **Extracción estructurada:**
   - proveedor local determinista para desarrollo y evaluación sin costo;
   - adaptador de Nebius Token Factory para ejecutar Nemotron cuando haya credenciales y autorización.
4. **Motor de políticas deterministas:** controla campos críticos, evidencia, severidad y condiciones que requieren escalamiento. El modelo no puede desactivar estos controles.
5. **Memoria por lote:** SQLite conserva recorridas, observaciones, tareas, decisiones y auditoría.
6. **Tavily opcional:** búsqueda permitida únicamente para preguntas externas justificadas, con lista de dominios y trazabilidad de fuentes. Permanece desactivada sin credenciales.
7. **Aprobación humana:** las propuestas de decisión no se ejecutan automáticamente; se aprueban o rechazan y queda registro.

La descripción completa está en `docs/architecture.md`.

## Qué está construido

- API y aplicación web responsive.
- Alta y consulta de lotes.
- Creación de recorridas.
- Carga de observaciones por texto o voz del navegador.
- Extracción de hallazgos estructurados con referencia a la nota original.
- Detección de datos críticos faltantes.
- Alertas justificadas y diferenciación entre evidencia e inferencia.
- Creación y priorización de tareas.
- Propuestas de decisión con aprobación o rechazo humano.
- Registro de auditoría.
- Proveedor local determinista.
- Adaptador de Nebius/Nemotron configurable por variables de entorno.
- Conector Tavily opcional con límites de uso.
- Fixtures agronómicos y evaluador reproducible.
- Pruebas unitarias y de integración.
- Documentación de arquitectura, evaluación, preparación de entrega y guion de video.
- Licencia Apache-2.0 y archivo de ejemplo de variables de entorno.

## Mapa de archivos

- `README.md`: instalación, ejecución, alcance y arquitectura resumida.
- `src/agrofield_agent/`: código principal.
- `src/agrofield_agent/main.py`: aplicación FastAPI y endpoints.
- `src/agrofield_agent/providers/`: proveedor local y adaptador Nebius/Nemotron.
- `src/agrofield_agent/policy.py`: reglas deterministas y controles de seguridad.
- `src/agrofield_agent/database.py`: persistencia SQLite.
- `src/agrofield_agent/evaluate.py`: evaluación del conjunto de casos.
- `src/agrofield_agent/static/`: interfaz web.
- `fixtures/eval_cases.jsonl`: casos de evaluación.
- `tests/`: pruebas automáticas.
- `docs/official-rules-freeze.md`: bases y fuentes oficiales congeladas.
- `docs/idea-landscape-matrix.md`: comparación de ideas y decisión.
- `docs/architecture.md`: arquitectura y límites de confianza.
- `docs/evaluation-spec.md`: métricas y criterios de aceptación.
- `docs/submission-readiness.md`: faltantes para la entrega pública.
- `docs/video-outline.md`: guion preliminar del video de menos de tres minutos.
- `reports/baseline.json`: resultado reproducible del baseline local.

## Cómo ejecutar localmente

Desde PowerShell:

```powershell
cd "C:\Users\Fly Agro\Documents\Codex\2026-09-01\nebius-nvidia-agrofield-agent\outputs\agrofield-agent"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m agrofield_agent
```

Luego abrir la dirección indicada por el servidor, normalmente `http://127.0.0.1:8000`.

Pruebas y evaluación:

```powershell
pytest -q
python -m agrofield_agent.evaluate fixtures/eval_cases.jsonl
```

No copiar credenciales dentro del repositorio. Usar las variables documentadas en `.env.example`.

## Estado de verificación

En la última verificación local:

- **8 pruebas aprobadas**.
- **12 casos** en el conjunto de evaluación.
- Precisión de extracción: **0,9884**.
- Recall de extracción: **0,9239**.
- F1 micro de extracción: **0,9551**.
- Recall de omisiones críticas: **1,0**.
- Tasa de afirmaciones no respaldadas: **0,0**.
- Seguridad de los bloqueos de decisión: **1,0**.
- NDCG de priorización: **1,0**.
- Latencia local p50: **0,071 ms**.
- Costo estimado del baseline: **US$0**.

Advertencia importante: estos números corresponden a un **baseline determinista local**, no a Nemotron y no a un benchmark revisado por agrónomos. No deben presentarse como evidencia de validez en producción.

## Lo que todavía no se hizo

- No se realizaron entrevistas reales con asesores o productores.
- No se validaron los casos y las prioridades con agrónomos independientes.
- No se ejecutó una evaluación con Nemotron en Nebius.
- No se verificaron latencia y costo reales de Token Factory o AI Cloud desde Argentina.
- No se ejecutó Tavily en runtime real.
- No hay autenticación, multiusuario ni aislamiento entre organizaciones.
- La persistencia sigue siendo SQLite local.
- El reconocimiento de voz depende del navegador y no constituye por sí mismo una integración NVIDIA.
- No hay URL pública.
- El repositorio no fue hecho público.
- No se grabó ni publicó el video.
- No se registró una submission.

## Riesgos y principios que no deben romperse

- El sistema ayuda a ordenar una recorrida; **no reemplaza el juicio profesional ni emite una prescripción agronómica autónoma**.
- Los bloqueos críticos deben seguir siendo deterministas y verificables.
- Toda alerta debe enlazar con evidencia, una regla o una fuente externa identificable.
- No convertir ausencia de evidencia en evidencia de ausencia.
- Mantener separados los hechos observados, las inferencias y las recomendaciones.
- Las decisiones sensibles requieren aprobación humana explícita.
- No enviar datos del lote a búsquedas externas sin necesidad y consentimiento.
- No incorporar secretos, tokens o datos personales en commits, fixtures, capturas o videos.
- Tavily no debe usarse si una regla o dato local resuelve el problema con mayor trazabilidad.

## Próximos pasos recomendados

1. Entrevistar entre tres y cinco asesores/productores y documentar el flujo real, los datos críticos y el costo de una omisión.
2. Revisar los 12 casos existentes con un agrónomo y ampliar el conjunto a por lo menos 30 casos, incluyendo negativos difíciles y notas ambiguas.
3. Con autorización y un límite de gasto explícito, ejecutar el mismo benchmark con uno o más modelos Nemotron disponibles en Nebius.
4. Comparar exactitud, omisiones, latencia y costo contra el baseline local; conservar ejemplos de errores.
5. Decidir con evidencia si Tavily mejora una parte concreta del flujo, por ejemplo verificación normativa o consulta de etiquetas oficiales.
6. Mejorar autenticación, privacidad, manejo de fallos y experiencia móvil antes de una URL pública.
7. Preparar demo, README final, formulario y video, pero publicar o enviar solamente después de autorización expresa.

## Instrucciones para la IA que continúe

Antes de modificar código:

1. Leer `README.md`, `docs/official-rules-freeze.md`, `docs/architecture.md`, `docs/evaluation-spec.md` y `docs/submission-readiness.md`.
2. Ejecutar las pruebas y reproducir `reports/baseline.json`.
3. Revisar `git status` y preservar cualquier cambio del usuario.
4. No sustituir las reglas deterministas por decisiones libres del modelo.
5. No afirmar que Nemotron fue probado mientras el proveedor reportado sea `local/deterministic-es-v0.1`.
6. No publicar, desplegar, generar costos, hacer público el repositorio ni enviar la participación sin autorización expresa.
7. Solicitar autorización antes de usar credenciales o servicios pagos, y proponer un límite de gasto.

### Prompt breve de reanudación

> Continúa el proyecto AgroField Agent desde este repositorio. Primero lee el README y la documentación señalada en `HANDOFF_PARA_OTRA_IA.md`, verifica el estado de Git y ejecuta las pruebas. Conserva los controles deterministas, la trazabilidad y la aprobación humana. No publiques, despliegues, consumas servicios pagos, hagas público el repositorio ni registres una submission sin autorización expresa. Distingue siempre el baseline local de cualquier resultado real con Nemotron. Informa qué encontraste y propone el siguiente incremento vertical verificable antes de hacer cambios amplios.

## Criterio de éxito final

Una demo competitiva debería mostrar, en menos de tres minutos, que una nota de campo incompleta se transforma en una recorrida estructurada; que el agente detecta una omisión importante, justifica una alerta, prioriza una tarea y bloquea una decisión hasta obtener aprobación humana. La evaluación y el video deben demostrar que esa conducta es reproducible, medible y ejecutada con Nemotron en Nebius.
