# Reportes

`local-candidate-2026-09-01.json` fue generado con:

```bash
python -m agrofield_agent.evaluate benchmark/agronomy_blind_v1/data/cases.jsonl \
  --report benchmark/agronomy_blind_v1/reports/local-candidate-2026-09-01.json
```

El proveedor es `local/deterministic-es-v0.1` y la referencia es `provisional_candidate_reference`. El reporte no es un resultado Nemotron y no constituye validación agronómica.

La latencia puede variar entre ejecuciones; las métricas funcionales y el inventario de fallos deben reproducirse con el mismo commit.
