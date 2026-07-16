# H8 - Machine Learning

## Objetivo

Implementar un baseline supervisado reproducible que aproxime las decisiones generadas por H6 utilizando el dataset H7.

## Principio metodológico

H8 no reemplaza el Recommendation Engine determinístico. El modelo cumple el rol `supervised_baseline_approximating_h6`.

## Componentes

- `TrainModel`.
- `DecisionTreeTrainingBackend`.
- Descubrimiento e importación histórica.
- Validación del dataset.
- Persistencia con `joblib`.
- Reporte JSON.
- Integración CLI.

## Algoritmo

```text
DecisionTreeClassifier
```

## Salvaguardas

Antes de entrenar se valida:

- esquema compatible;
- cantidad mínima de filas;
- columna objetivo;
- al menos dos clases;
- ejemplos suficientes por clase.

El sistema no genera datos sintéticos ni publica métricas cuando el entrenamiento no es válido.

## Ejecución

```powershell
pde train-model `
  --dataset examples/output/dataset.csv `
  --model examples/output/model.joblib `
  --report examples/output/training_report.json
```

## Artefactos

- `model.joblib`.
- `training_report.json`.

## Limitaciones

- Aprende etiquetas H6.
- Depende del tamaño y diversidad del histórico.
- No deben reportarse resultados definitivos con datos no representativos.

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

H9 — Explainability
