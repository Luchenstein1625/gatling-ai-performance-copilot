# H10 - Local End-to-End Integration PoC

## Objetivo

Integrar los componentes implementados en H1–H9 dentro de una única Proof of Concept local, reproducible y ejecutable mediante CLI.

H10 no se conecta con plataformas, redes, pipelines ni servicios internos del banco.

## Alcance

El hito incorpora:

- un comando end-to-end;
- normalización de la ejecución;
- recomendación determinística;
- incorporación de una fila al dataset;
- entrenamiento opcional;
- explicación opcional del modelo;
- resumen JSON;
- reporte HTML autocontenido;
- manejo controlado de datasets insuficientes.

## Fuera de alcance

- Azure DevOps;
- GitHub Enterprise corporativo;
- APIM;
- AKS;
- secretos corporativos;
- autenticación;
- ejecución remota de Gatling;
- datos productivos;
- dashboard persistente;
- PDF;
- integración con plataformas del banco.

## Componentes

```text
application/use_cases/run_pipeline.py
infrastructure/reporting/html_report_generator.py
interfaces/cli/pipeline.py
tests/test_run_pipeline.py
tests/test_html_report_generator.py
```

## Integración CLI

`main.py` registra el comando mediante:

```python
from performance_decision_engine.interfaces.cli.pipeline import (
    register_pipeline_command,
)

register_pipeline_command(app, console)
```

## Flujo

```text
performance.yaml
        +
parametricConfigurationValues.yaml
        +
global_stats.json
        +
assertions.json (opcional)
        │
        ▼
RunPipeline
        │
        ├── NormalizeExecution
        ├── RecommendExecution
        └── GenerateDatasetRow
        │
        ▼
Artefactos base
        │
        ├── execution_summary.json
        ├── recommendation.json
        └── dataset.csv
        │
        ▼
Entrenamiento opcional
        │
        ├── model.joblib
        ├── training_report.json
        └── model_explanation.json
        │
        ▼
pipeline_summary.json
        +
report.html
```

## Ejecución básica

```powershell
pde pipeline `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output-dir examples/output/pipeline
```

## Con assertions

```powershell
pde pipeline `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --assertions examples/input/assertions.json `
  --output-dir examples/output/pipeline
```

## Con entrenamiento

```powershell
pde pipeline `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output-dir examples/output/pipeline `
  --train
```

## Manejo de entrenamiento no válido

El pipeline no inventa modelos ni métricas.

Cuando H8 rechaza el dataset, el resultado queda registrado como:

```json
{
  "status": "skipped",
  "reason": "..."
}
```

La razón queda disponible en:

- `pipeline_summary.json`;
- `report.html`.

## Reporte HTML

El reporte es autocontenido y no utiliza servicios externos.

Incluye:

- recomendación;
- explicación;
- regla activadora;
- métricas principales;
- endpoints configurados;
- traza de decisión;
- warnings;
- estado del entrenamiento;
- explicación global disponible;
- limitaciones de la PoC.

## Criterios de aceptación

- `pde pipeline` aparece en la ayuda CLI;
- el flujo base se ejecuta con un solo comando;
- se generan los cinco artefactos obligatorios;
- se conserva la recomendación H6;
- se genera una fila H7;
- H8 y H9 se ejecutan solo cuando es válido;
- el reporte HTML escapa contenido externo;
- no se requieren servicios externos;
- los quality gates pasan.

## Validación

```powershell
pde --help
pde pipeline --help
black --check .
ruff check .
mypy src
pytest -v
```

## Estado

✅ Completado para PoC local

## Evolución futura

La integración con plataformas corporativas deberá implementarse mediante adaptadores nuevos, sin modificar el dominio ni los casos de uso existentes.
