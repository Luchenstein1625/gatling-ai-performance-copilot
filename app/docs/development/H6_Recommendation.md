# H6 – Recommendation Engine

## Objetivo

Implementar una recomendación baseline a partir del modelo canónico `NormalizedExecution`, sin
acoplar el dominio a YAML, JSON, Gatling, Typer o FastAPI.

## Diseño

H6 reutiliza la entidad `Recommendation` y la función `recommend_baseline` existentes. No introduce
una nueva jerarquía de entidades, value objects, reglas o repositorios.

Flujo:

```text
NormalizedExecution
        │
        ▼
RecommendExecution
        │
        ▼
recommend_execution
        │
        ▼
Recommendation
```

## Reglas iniciales

La recomendación es `review` cuando:

- no existen endpoints habilitados;
- la ejecución no contiene requests;
- existen requests fallidos;
- alguna assertion falla;
- el p95 no está disponible;
- no existe un objetivo de tiempo de respuesta resuelto;
- el p95 supera el objetivo configurado.

La recomendación es `maintain` cuando la ejecución dispone de datos suficientes y no se detectan
incumplimientos.

## Alcance de las métricas

Las métricas de `NormalizedExecution` son globales. Cuando existen varios endpoints habilitados, H6
utiliza el objetivo de tiempo de respuesta más estricto y registra que el resultado no puede atribuirse
a un endpoint individual.

## CLI

```powershell
pde recommend `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output examples/output/recommendation.json
```

`--assertions` y `--output` son opcionales.

## API

```text
POST /recommendations
```

El cuerpo corresponde a un `NormalizedExecution` y la respuesta utiliza la entidad existente
`Recommendation`.

## Archivos

Nuevos:

- `application/use_cases/recommend_execution.py`
- `tests/test_recommend_execution.py`
- `docs/development/H6_Recommendation.md`

Modificados:

- `domain/services/baseline_service.py`
- `interfaces/cli/main.py`
- `interfaces/api/main.py`

## Definition of Done

- Se conserva la compatibilidad de `Recommendation` y `recommend_baseline`.
- El dominio recibe `NormalizedExecution`.
- No se inventan niveles ni valores de configuración.
- CLI y API exponen la recomendación.
- Las pruebas anteriores continúan funcionando.
- Las pruebas nuevas aprueban.
- Black, Ruff, MyPy y Pytest finalizan sin errores.
