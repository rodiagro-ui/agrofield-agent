# AgroField Agent — handoff operativo para otra IA

> Snapshot: 2 de septiembre de 2026. Repositorio local, privado, sin despliegue ni costos. Existe una autorización limitada para correos enviados por el usuario; este documento no la amplía ni autoriza a la IA a contactar personas.

## Estado verificable

- Rama: `main`.
- MVP base: `32855c4` — `Build AgroField Agent vertical MVP`.
- Separación Fase A/B: `4390a4c`.
- Gates humanos estrictos: `19ab37f`.
- Freeze candidato P0-closed: `42f4e97`.
- Sensibilidad de exposición e independencia global de roles: `1bd5a0e`.
- Autorización humana limitada registrada: `ff65472`.
- Freeze prehumano vigente: `bee339e`.
- HEAD efectivo: ejecutar `git log -1 --oneline`, porque el commit de este handoff será posterior.
- Licencia: MIT.
- Tests: 44/44 aprobados en la última verificación.
- Freeze candidato prehumano vigente: 34/34 hashes válidos.
- `src/agrofield_agent/policy.py`: sin cambios respecto del MVP; hash canónico `e659fb913cc7526d4c9673e7ce6460ba83abce310a9fe8e0d94dbd3900d9938b`.

Estado externo exacto:

- entrevistas reales: 0;
- personas contactadas mediante invitación: 1;
- revisiones primarias reales: 0/30;
- revisiones secundarias reales: 0/10;
- revisiones de salida reales: 0/30 primarias y 0/10 secundarias;
- adjudicaciones reales: 0/30;
- llamadas Nebius: 0;
- llamadas Tavily: 0;
- costo: US$0;
- publicación, despliegue, video y submission: no realizados;
- invitaciones enviadas: 1/5 de entrevista y 0/3 de revisión;
- aceptaciones confirmadas: 0;
- configuración privada: no atestiguada ante la IA; estado real desconocido;
- desviación saneada: `DV-OUTREACH-001`, documentada en `benchmark/agronomy_blind_v1/authorization/outreach-status-2026-09-02.md`;
- autorización humana: `AUTHORIZED_EMAIL_ONLY_PENDING_PRIVATE_SETUP`.

## Lectura obligatoria

Antes de actuar, leer completos y en este orden:

1. `README.md`
2. `docs/research/official-rules-freeze-2026-09-01.md`
3. `docs/architecture.md`
4. `docs/evaluation/evaluation-spec.md`
5. `docs/submission-readiness.md`
6. `docs/research/landscape-and-idea-matrix.md`
7. `docs/video-outline.md`
8. `HANDOFF_PARA_OTRA_IA.md`
9. `RESUMEN_COMPLETO_PARA_OTRA_IA.md`
10. `benchmark/agronomy_blind_v1/authorization/README.md`
11. `benchmark/agronomy_blind_v1/authorization/preflight-findings.md`
12. `benchmark/agronomy_blind_v1/authorization/authorization-decision-2026-09-02.md`
13. `benchmark/agronomy_blind_v1/authorization/email-outreach-pack.md`
14. `benchmark/agronomy_blind_v1/authorization/outreach-status-2026-09-02.md`

Después ejecutar:

```powershell
git status --short --branch
git log --oneline -10
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m agrofield_agent.evaluate fixtures/eval_cases.jsonl
.\.venv\Scripts\python.exe -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl
.\.venv\Scripts\python.exe -m agrofield_agent.freeze benchmark/agronomy_blind_v1/freeze/manifest.json --root .
```

## Producto

AgroField Agent es un agente operativo para recorridas de soja posteriores a lluvia intensa, granizo o viento. Convierte una nota por texto o voz del navegador en hechos estructurados con citas, omisiones críticas, prioridades y tareas. Las reglas deterministas deciden completitud y bloqueos; las decisiones sensibles permanecen pendientes hasta aprobación humana auditada.

No es un chatbot generalista ni un prescriptor autónomo. El diferenciador es demostrar que existe evidencia suficiente antes de actuar.

Arquitectura ya construida:

- FastAPI + interfaz web móvil;
- SQLite con memoria por lote y auditoría;
- extractor local determinista sin costo;
- adaptador Nebius/Nemotron preparado, nunca ejecutado;
- `policy.py` como autoridad de seguridad;
- aprobación humana obligatoria;
- Tavily opcional, restringido y nunca ejecutado.

## Resultados locales que no deben confundirse

Baseline heredado, 12 fixtures sintéticos, proveedor `local/deterministic-es-v0.1`:

| Métrica | Valor |
|---|---:|
| Precisión | 0,9884 |
| Recall | 0,9239 |
| F1 micro | 0,9551 |
| Recall de omisiones críticas | 1,0000 |
| Afirmaciones no respaldadas | 0,0000 |
| Cobertura de citas | 1,0000 |
| Seguridad de bloqueo | 1,0000 |
| Integridad de aprobación | 1,0000 |
| nDCG | 1,0000 |
| Fallos adversos | 8 |

Benchmark candidato, 30 casos sintéticos, referencia provisional:

| Métrica | Valor |
|---|---:|
| Precisión | 0,9851 |
| Recall | 0,8609 |
| F1 micro | 0,9188 |
| Recall de omisiones críticas | 0,9714 |
| Afirmaciones no respaldadas | 0,0050 |
| Cobertura de citas | 1,0000 |
| Seguridad de bloqueo | 1,0000 |
| Integridad de aprobación | 1,0000 |
| nDCG | 0,9877 |
| Task precision humana | no disponible |
| Fallos adversos | 53 |
| `benchmark_validated` | `false` |

Ambos resultados son locales y sintéticos. No son resultados Nemotron ni evidencia agronómica humana.

## Cierre de P0 y P1

1. **Anclaje de referencia:** Fase A y Fase B son archivos distintos. Fase A contiene solo nota/contexto. Fase B se vincula al hash canónico de la anotación Fase A del mismo revisor.
2. **Gate incompleto:** `benchmark_validated` depende ahora de 17 gates explícitos con valor, requisito y razón de fallo. `--require-validated` sale con código 2 si falla uno.
3. **Formularios vacíos:** esquema `1.1.0-candidate` valida IDs, asignación, fecha, privacidad, evidencia, campos, tareas y estados. Las plantillas vacías no cuentan y se registran como inválidas.
4. **Task precision duplicada:** la métrica vinculante es `primary_task_precision`; la secundaria solo mide acuerdo. `adjudicated_task_precision` permanece separado y `null` hasta existir.
5. **Dobles de salida ausentes:** se exigen 30 salidas primarias y 10 secundarias completas, mismas salida/alias, revisores distintos y locks válidos. El reporte lista IDs faltantes.
6. **Exposición previa:** el resultado vinculante conserva todos los pares; una sensibilidad separada recalcula referencia y salida sin pares donde cualquiera declaró exposición.
7. **Superposición de roles:** un ID no puede cruzarse entre primario/secundario ni entre revisor/adjudicador en ningún caso de la ronda. El cruce se reporta y bloquea readiness.

Pruebas relevantes:

- Fase A rechaza claves de salida y ambos paquetes no pueden compartir destino;
- hash Fase A alterado bloquea completitud;
- las cuatro plantillas incompletas se rechazan;
- una secundaria insegura no cambia la precisión primaria;
- quitar una sola salida secundaria hace fallar `--require-validated` con código 2;
- cada gate falla de forma independiente;
- fixture positivo completo 30/10 prueba la ruta feliz, marcado `test_fixture_only` y nunca tratado como evidencia humana.
- tests adversos prueban exposición declarada y cruces de roles entre casos.

## Freeze

- `benchmark/agronomy_blind_v1/freeze/manifest-v1.0.0-candidate.json` conserva exactamente el freeze histórico de 18 artefactos.
- `manifest-v1.1.0-candidate.json` y `manifest-v1.2.0-authorized-prehuman.json` preservan los freezes intermedios exactos.
- `benchmark/agronomy_blind_v1/freeze/manifest.json` es el freeze vigente `1.2.1-authorized-prehuman`, 34/34 hashes.
- El vigente declara `candidate_only: true`, `human_validated: false`, `benchmark_validated: false`, 0 contactos y `authorization: AUTHORIZED_EMAIL_ONLY_PENDING_PRIVATE_SETUP`.
- Esos conteos describen el instante del freeze. La invitación `I01` ocurrió después y se registra fuera del manifiesto; no se reescribe un snapshot histórico.
- El reporte asociado es `benchmark/agronomy_blind_v1/reports/local-candidate-prehuman-v1.2-2026-09-02.json`.
- Un futuro freeze humano debe ser un manifiesto nuevo con `freeze_scope: human_reviewed_benchmark_inputs`; nunca se reetiqueta el candidato.

## Reglas inviolables

- No modificar ni debilitar `policy.py` para mejorar métricas.
- Mantener hechos → inferencias → recomendaciones.
- No convertir falta de evidencia en evidencia de ausencia.
- Toda alerta debe enlazar nota, regla o fuente identificable.
- Toda decisión sensible requiere aprobación nominada y auditoría.
- No inventar entrevistas, revisiones, acuerdos o etiquetas humanas.
- Cero datos personales, nombres, establecimientos o coordenadas exactas en Git.
- En adelante, solo el usuario envía correos dentro de los cupos autorizados y después del setup privado. Tras `DV-OUTREACH-001`, la IA no debe recibir nuevos destinatarios, PII ni notas crudas.
- No publicar, desplegar, consumir Nebius/Tavily, gastar, subir video ni enviar la submission sin autorización expresa.
- Antes de un servicio potencialmente pago: autorización separada y límite de gasto concreto.

## Única debilidad crítica residual

La cadena de evidencia externa sigue vacía. El arnés ya es defendible, pero los 30 casos y todas sus referencias siguen siendo sintéticos. Sin 3–5 entrevistas y revisión independiente 30/10, las cifras son hipótesis de ingeniería, no prueba de impacto o corrección agronómica.

## Siguiente acción permitida

Antes de cualquier contacto adicional, el usuario atestigua sin PII que completó fuera de Git los siete puntos del gate privado de `email-outreach-pack.md`: responsable/contacto/domicilio, destinatarios, almacenamiento, retención, canal de derechos, `PR01` independiente y mapa de códigos. Ya se consumió el slot de entrevista `I01`; quedan como máximo 4 invitaciones de entrevista y 3 de revisión.

La IA espera solo el parte sin PII definido en `outreach-status-2026-09-02.md`. Después: invitaciones restantes → consentimientos privados → entrevistas → saneamiento `DS01` + revisión `PR01` → Fase A 30/10 → locks → Fase B 30/10 → acuerdo y sensibilidad → adjudicación 30 → freeze humano → `--require-validated`. Recién entonces se solicita autorización y presupuesto para Nemotron.
