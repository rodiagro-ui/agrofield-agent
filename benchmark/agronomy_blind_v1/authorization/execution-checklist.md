# Checklist de ejecución y cierre

## A. Autorización

- [ ] El usuario respondió con autorización expresa y límites.
- [ ] Máximo de invitaciones y canales quedaron definidos.
- [ ] Remitente humano y custodio privado fueron designados.
- [ ] Responsable, contacto, domicilio, destinatarios y retención se completaron fuera de Git.
- [ ] Grabación y compensación están en `NO` o tienen autorización separada.
- [ ] Se confirmó que esta autorización no incluye servicios pagos ni publicación.

## B. Preflight técnico

- [x] Se resolvieron todos los P0 de `preflight-findings.md` (`4390a4c`, `19ab37f`).
- [x] Tests nuevos prueban que el paquete de referencia no contiene salida, alias, proveedor, split ni referencia.
- [x] Tests prueban que una plantilla vacía/incompleta no cuenta como revisión.
- [x] Task precision no duplica etiquetas del segundo revisor.
- [x] `--require-validated` verifica entrevistas, privacidad, 30 primarias, 10 dobles de referencia y salida, adjudicación, umbrales y freeze final.
- [x] `policy.py` continúa sin cambios.

## C. Reclutamiento

- [ ] Cada invitación fue privada y dentro del cupo.
- [ ] Se registró solo en el mapa privado.
- [ ] Se envió como máximo un recordatorio.
- [ ] Rechazos y retiros se cerraron sin insistencia.
- [ ] Hay 3–5 entrevistas confirmadas.
- [ ] Hay dos revisores agronómicos independientes confirmados.
- [ ] Hay un adjudicador distinto o se documentó la limitación de adjudicación conjunta.

## D. Entrevistas

- [ ] Se leyó el addendum privado y el consentimiento existente.
- [ ] Cada alcance se aceptó o rechazó por separado.
- [ ] No se grabó.
- [ ] La primera mitad no reveló IA, alertas ni bloqueos.
- [ ] Se registró evidencia contraria con el mismo detalle.
- [ ] Las notas crudas quedaron fuera de Git.
- [ ] `DS01` saneó y `PR01` revisó de forma independiente.
- [ ] Solo registros `passed` se incorporaron.

## E. Ronda ciega — Fase A

- [ ] `R01` y `R02` aceptaron publicación anónima de resultados.
- [ ] Se asignaron IDs aleatorios sin iniciales.
- [ ] Se entregaron únicamente nota, contexto sintético y rúbrica.
- [ ] No se mostró salida, alias, split ni referencia candidata.
- [ ] `R01` completó 30 referencias.
- [ ] `R02` completó los 10 IDs prefijados.
- [ ] Los archivos se validaron, bloquearon y hashearon antes de Fase B.

## F. Ronda ciega — Fase B

- [ ] Alias aleatorio y mapa privado preparados.
- [ ] `R01` revisó salidas y todas las tareas de 30 casos.
- [ ] `R02` revisó salidas y todas las tareas de los 10 dobles.
- [ ] Ningún revisor vio proveedor, split, métricas o respuestas ajenas.
- [ ] Se registraron E1–E8 y severidad.
- [ ] Los archivos se validaron, bloquearon y hashearon.

## G. Acuerdo y adjudicación

- [ ] Desacuerdo bruto y Cohen’s kappa se calcularon antes de revelar respuestas cruzadas.
- [ ] Acuerdo numérico se reportó sin kappa nominal.
- [ ] Acuerdo de clasificación de tareas usa los 10 pares completos.
- [ ] Los resultados bajos y casos adversos se preservaron.
- [ ] `A01` revisó los 30 casos y dejó decisión/rationale.
- [ ] Para los 10 dobles, cada adjudicación referencia ambos review IDs.
- [ ] Ninguna revisión original se sobrescribió.

## H. Gates y freeze humano

- [ ] Entrevistas consentidas y saneadas: 3–5.
- [ ] Revisiones primarias: 30/30.
- [ ] Revisiones dobles: 10/10 en referencias y salidas.
- [ ] Task precision adjudicada/primaria: ≥0,90.
- [ ] Critical omission recall: ≥0,98.
- [ ] Unsupported assertion rate: ≤0,01.
- [ ] Decision gate safety: 1,00.
- [ ] Evidence quote coverage: 1,00.
- [ ] Human approval integrity: 1,00.
- [ ] Holdout no usado para modificar sistema o umbrales.
- [ ] Escaneo de privacidad final aprobado.
- [ ] `--require-validated` finaliza con código 0.
- [ ] Se creó un manifiesto humano nuevo; el freeze candidato no se sobrescribió.
- [ ] Todos los hashes del nuevo manifiesto coinciden.

## I. Informe honesto

- [ ] Se distingue entrevista exploratoria de muestra representativa.
- [ ] Se reportan cantidad, roles y bandas de experiencia sin identidades.
- [ ] Se declaran desacuerdo, exposición previa y conflictos.
- [ ] Se separan baseline local y futuros resultados Nemotron.
- [ ] No se afirma reducción real de costos o errores sin medición correspondiente.
- [ ] No se inicia Nemotron/Tavily ni publicación sin una nueva autorización.
