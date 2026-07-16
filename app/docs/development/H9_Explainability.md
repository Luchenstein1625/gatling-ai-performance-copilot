# H9 - Explainability

## Objetivo

Explicar por qué el sistema produce una recomendación y cómo el modelo H8 utiliza las variables.

## Niveles de explicación

1. Traza de reglas determinísticas H6.
2. Explicación global del árbol H8.

## Baseline determinístico

Cada recomendación incorpora:

- `decision_trace`;
- regla evaluada;
- resultado;
- valor observado;
- valor esperado;
- `triggered_rule`.

## Modelo H8

El caso de uso `ExplainModel` utiliza un puerto desacoplado y genera:

- versión de esquema;
- tipo y rol del modelo;
- clases;
- columnas originales y transformadas;
- importancia de variables;
- reglas textuales;
- `random_state`;
- limitaciones.

## Flujo

```text
model.joblib
        │
        ▼
Validación del artefacto
        │
        ▼
ExplainModel
        │
        ▼
model_explanation.json
```

## Ejecución

```powershell
pde explain-model `
  --model examples/output/model.joblib `
  --output examples/output/model_explanation.json
```

## Seguridad

`joblib` puede ejecutar código durante la carga. Solo deben utilizarse artefactos confiables generados por este proyecto.

## Garantías

- La explicación no modifica el modelo.
- La importancia se ordena de forma estable.
- Las reglas se exportan como texto.
- Las limitaciones quedan registradas.

## Limitaciones

- La explicación es global, no local por predicción.
- El árbol aproxima etiquetas H6.
- La explicación no demuestra causalidad.

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

H10 — Integration
