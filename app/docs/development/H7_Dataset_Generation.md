# H7 – Dataset Generation

## Estado

✅ Completado

## Objetivo

Transformar una ejecución normalizada y la decisión determinística de H6 en una fila estable,
reproducible y preparada para Machine Learning.

## Diseño

H7 reutiliza:

- `NormalizedExecution`;
- `Recommendation`;
- `RecommendExecution`;
- `GenerateDatasetRow`;
- el comando CLI existente.

No introduce entidades, Value Objects, DTO, repositorios ni dependencias de Machine Learning.

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

## Contrato del dataset

- Una ejecución equivale a una fila.
- `schema_version` identifica el contrato.
- `metrics_scope` permanece en `execution`.
- `recommendation_action` es la etiqueta generada por H6.
- Los valores ausentes se mantienen como valores ausentes.
- No se inventan criticidad, complejidad ni cuadrantes.
- El encabezado existente se valida antes de anexar una fila.

## Archivos

### Nuevos

- `application/use_cases/generate_dataset.py`
- `tests/test_generate_dataset.py`
- `docs/development/H7_Dataset_Generation.md`

### Modificados

- `interfaces/cli/main.py`
- documentación de estado y roadmap

## Pruebas

H7 agrega pruebas para:

- generación estable de una fila;
- agregaciones incompletas;
- assertions opcionales.

Estado final:

- Black ✅
- Ruff ✅
- MyPy ✅
- Pytest ✅
- 53 pruebas aprobadas

## Riesgos conocidos

- Las métricas siguen siendo globales.
- La etiqueta H6 es determinística.
- Un CSV pequeño o con una sola clase no es suficiente para entrenar H8.
- H7 no demuestra todavía capacidad predictiva.

## Compatibilidad

H1–H6 permanecen compatibles.

## Definition of Done

- El esquema es estable y versionado.
- La fila sólo utiliza datos existentes.
- La etiqueta proviene de H6.
- El CSV valida su encabezado.
- Los quality gates aprueban.
- H8 puede consumir el dataset sin modificar H5–H7.
