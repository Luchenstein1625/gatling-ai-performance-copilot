# H6 – Decision Matrix

## Estado

✅ Completado

## Objetivo

Implementar una matriz de decisión determinística que evalúe una ejecución normalizada y produzca
una recomendación reproducible, sin acoplar el dominio a YAML, JSON, Gatling, Typer o FastAPI.

H6 conserva el roadmap original:

- H5 – Normalization;
- H6 – Decision Matrix;
- H7 – Dataset Generation;
- H8 – Machine Learning;
- H9 – Explainability;
- H10 – Integration.

## Diseño

H6 reutiliza `NormalizedExecution`, `Recommendation`, `RecommendExecution`,
`recommend_execution`, `recommend_baseline` y la matriz 3×3 existente de `resolve_quadrant`.

No introduce nuevas entidades, Value Objects, DTO, repositorios ni servicios.

```text
NormalizedExecution
        │
        ▼
RecommendExecution
        │
        ▼
Decision Matrix
        │
        ▼
Recommendation
```

## Reglas de decisión

La decisión es `review` cuando:

- no existen endpoints habilitados;
- la ejecución no contiene requests;
- existen requests fallidos;
- alguna assertion falla;
- el p95 no está disponible;
- no existe un objetivo de tiempo de respuesta resuelto;
- el p95 supera el objetivo configurado.

La decisión es `maintain` cuando la ejecución dispone de datos suficientes y no se detectan
incumplimientos.

## Matriz de cuadrantes existente

| Complejidad / Criticidad | low | medium | high |
|---|---:|---:|---:|
| low | 1 | 2 | 3 |
| medium | 4 | 5 | 6 |
| high | 7 | 8 | 9 |

La matriz existente no se duplica ni se reemplaza.

## Alcance de las métricas

Las métricas de `NormalizedExecution` son globales. Cuando existen varios endpoints habilitados,
H6 utiliza el objetivo de tiempo de respuesta más estricto y registra que el resultado no puede
atribuirse a un endpoint individual.

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

## Archivos reutilizados

- `application/use_cases/recommend_execution.py`
- `domain/services/baseline_service.py`
- `domain/services/quadrant_service.py`
- `domain/entities/recommendation.py`
- `interfaces/cli/main.py`
- `interfaces/api/main.py`
- `tests/test_recommend_execute.py`

## Compatibilidad

- Compatible con H1–H5.
- No cambia el contrato público de `Recommendation`.
- No agrega dependencias externas.
- Mantiene CLI, API y JSON existentes.
- Deja disponible el baseline determinístico para H7 y H8.

## Definition of Done

- Se conserva la compatibilidad de `Recommendation` y `recommend_baseline`.
- El dominio recibe `NormalizedExecution`.
- Se reutiliza la matriz 3×3 existente.
- No se inventan niveles ni valores de configuración.
- CLI y API exponen la decisión.
- Las pruebas anteriores continúan funcionando.
- Black, Ruff, MyPy y Pytest finalizan sin errores.
- El siguiente hito oficial es H7 – Dataset Generation.
