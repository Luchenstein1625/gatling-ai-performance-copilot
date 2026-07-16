# H7 - Dataset Generation

## Objetivo

Generar un dataset tabular, estable y reproducible a partir de `NormalizedExecution` y `Recommendation`.

## Flujo

```text
NormalizedExecution
        +
Recommendation
        │
        ▼
GenerateDatasetRow
        │
        ▼
CSV schema version 1
```

## Componentes

- `GenerateDatasetRow`.
- Comando `pde dataset`.
- Escritor CSV incremental.
- Validación del encabezado.
- Esquema versionado.

## Contenido

- configuración agregada;
- métricas globales;
- percentiles;
- throughput;
- assertions;
- warnings;
- etiqueta `recommendation_action`.

## Garantías

- Una ejecución produce una fila.
- No se inventan datos ausentes.
- La etiqueta se obtiene desde H6.
- El encabezado debe coincidir con el esquema.

## Ejecución

```powershell
pde dataset `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output examples/output/dataset.csv
```

## Validación

```powershell
black --check .
ruff check .
mypy src
pytest -v
```

## Estado

✅ Completado

## Próximo hito

H8 — Machine Learning
