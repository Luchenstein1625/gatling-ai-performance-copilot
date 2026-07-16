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
| H10 – Local End-to-End Integration PoC | ✅ |

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

## Pipeline H10

```powershell
pde pipeline `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output-dir examples/output/pipeline
```

Con assertions:

```powershell
pde pipeline `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --assertions examples/input/assertions.json `
  --output-dir examples/output/pipeline
```

Con entrenamiento opcional:

```powershell
pde pipeline `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output-dir examples/output/pipeline `
  --train
```

## Flujo integrado

```text
NormalizeExecution
        │
        ▼
RecommendExecution
        │
        ▼
GenerateDatasetRow
        │
        ├──► TrainModel (opcional)
        │          │
        │          ▼
        │     ExplainModel
        │
        ▼
HtmlReportGenerator
```

## Artefactos obligatorios

```text
execution_summary.json
recommendation.json
dataset.csv
pipeline_summary.json
report.html
```

## Artefactos condicionales

```text
model.joblib
training_report.json
model_explanation.json
```

## Restricciones

- H6 es el baseline determinístico oficial.
- H8 aproxima etiquetas generadas por H6.
- H9 explica reglas y artefactos confiables H8.
- H10 integra el flujo, pero no reemplaza las validaciones anteriores.
- El entrenamiento puede quedar como `skipped`.
- La PoC no se conecta con plataformas del banco.
