# Performance Decision Engine

Implementación técnica de Gatling AI Performance Copilot.

## Estado

| Hito | Estado |
|---|:---:|
| H1 – Project Bootstrap | ✅ |
| H2 – Parameter Values | ✅ |
| H3 – Performance YAML | ✅ |
| H4 – Gatling Results | ✅ |
| H5 – Normalization | ✅ |
| H6 – Decision Matrix | ✅ |
| H7 – Dataset Generation | ✅ |
| H8 – Machine Learning | ✅ |
| H9 – Explainability | ✅ |
| H10 – Integration | ⏳ |

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Verificación

```powershell
pde doctor
pde --version
black --check .
ruff check .
mypy src
pytest -v
```

## CLI

### Normalizar

```powershell
pde normalize `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output examples/output/execution_summary.json
```

### Recomendar

```powershell
pde recommend `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output examples/output/recommendation.json
```

### Dataset H7

```powershell
pde dataset `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output examples/output/dataset.csv
```

### Entrenar H8

```powershell
pde train-model `
  --dataset examples/output/dataset.csv `
  --model examples/output/model.joblib `
  --report examples/output/training_report.json
```

### Explicar H9

```powershell
pde explain-model `
  --model examples/output/model.joblib `
  --output examples/output/model_explanation.json
```

## Artefactos

```text
execution_summary.json
recommendation.json
dataset.csv
model.joblib
training_report.json
model_explanation.json
```

## Restricciones

- H6 es el baseline determinístico oficial.
- H8 aproxima etiquetas de H6.
- H9 explica el baseline y el artefacto H8.
- El modelo no se entrena con una sola clase.
- Solo deben cargarse artefactos confiables.
