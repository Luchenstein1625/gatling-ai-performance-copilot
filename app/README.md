# Performance Decision Engine

## Pipeline integral del feedback evaluador

La versión completa incorpora cuatro capas: clasificación binaria de aplicabilidad,
decisión `review/maintain/upgrade`, recomendación controlada de parámetros y validación
offline/online. Se ejecuta sobre el histórico real con:

```powershell
pde evaluate-complete `
  --source "..\datasaet\resultadoPruebasGatling.txt" `
  --output-dir "..\Resultados\complete_feedback"
```

La salida incluye comparación de árbol de decisión, regresión logística, random forest y
baseline; matrices de confusión; reglas del árbol; configuración y cuadrante operacional
propuestos; y el estado `pending_new_execution` cuando falta validar la recomendación con
una nueva ejecución Gatling. Una falla siempre produce `review` y conserva la configuración.

La evaluación Pres3 ampliada también genera `threshold_cost_analysis.csv` con 17
cut-offs, `segment_metrics.csv` por pilar y componente, EDA por clase y validación
cruzada `GroupKFold` de cinco particiones por `Build_Id`. Los costos relativos por
defecto son supuestos configurables: falso `applies` = 10, falso `not_applies` = 2 y
revisión manual = 1; no representan pesos ni ahorro demostrado. La validación
experimental permanece en `pending_new_execution` hasta correr en Gatling una muestra
de configuraciones `upgrade`.

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

## Importación histórica (batch)

Si tus ejecuciones históricas están en `examples/input/sources`, el comando usa esa ruta por defecto:

- En cada ejecución se crea automáticamente una carpeta `run_YYYYMMDD_HHMMSS` dentro del directorio base del `--output`.
- El dataset CSV y el reporte JSON quedan dentro de esa carpeta para evitar sobreescrituras.

```powershell
pde dataset-batch `
  --output examples/output/historical_dataset.csv `
  --report examples/output/historical_batch_report.json `
  --replace
```

Ejemplo de resultado:

```text
examples/output/run_20260803_184501/historical_dataset.csv
examples/output/run_20260803_184501/historical_batch_report.json
```

Si quieres usar otra carpeta fuente:

```powershell
pde dataset-batch `
  --source <ruta_fuente> `
  --output examples/output/historical_dataset.csv `
  --report examples/output/historical_batch_report.json `
  --replace
```

## Evaluación automática completa (general + semillas)

Para no ejecutar paso a paso, este comando genera todo en una sola corrida:

- Crea carpeta `run_YYYYMMDD_HHMMSS`.
- Importa dataset histórico.
- Genera reportes generales (calidad, entrenamiento, explicación, evaluación multiseed).
- Genera reportes individuales por semilla en `seed_reports/seed_XX.json`.
- Actualiza un índice central de corridas en `examples/output/runs_index.json`.
- Genera comparador consolidado en `examples/output/runs_comparison_latest.json`.
- Genera informe de validez estadística en `statistical_validity_report.json` (IC 95% y evidencia por comparación).

```powershell
pde auto-evaluate `
  --source examples/input/sources `
  --output-base examples/output `
  --seeds 30 `
  --feature-profile operational_core
```

Regenerar el comparador consolidado desde el índice:

```powershell
pde compare-runs `
  --output-base examples/output
```

## Recomendación histórica de cuadrante (dataset corporativo)

El input real es `datasaet/resultadoPruebasGatling.txt`. El comando importa sus 6.000+
registros de ancho fijo, separa entrenamiento y prueba por `Build_Id` y compara árbol,
regresión logística y random forest para recomendar `review`, `maintain` o `upgrade`.

```powershell
pde evaluate-historical `
  --source ..\datasaet\resultadoPruebasGatling.txt `
  --output-dir examples\output\historical_recommendation
```

Artefactos generados:

- `historical_recommendation_evaluation.json`: matrices de confusión y precision/recall/F1 para
  entrenamiento y prueba de los tres modelos.
- `historical_recommendation_model.joblib`: mejor modelo según F1 de `review`.
- `historical_recommendation_dataset.csv`: versión normalizada y auditable del dataset.
- `decision_tree.dot` y `decision_tree_rules.txt`: árbol visualizable y reglas legibles.

Para renderizar el árbol si Graphviz está instalado:

```powershell
dot -Tpng examples\output\historical_recommendation\decision_tree.dot `
  -o examples\output\historical_recommendation\decision_tree.png
```

Las fallas y resultados irregulares siempre producen `review`; nunca `downgrade`. Un caso
exitoso puede producir `maintain` o proponer `upgrade`, pero el cambio de cuadrante requiere
validación humana. Las métricas posteriores crean la etiqueta histórica y luego se excluyen
de los predictores para evitar fuga de información.

## API de corridas

Endpoints para consultar trazabilidad y ranking sin revisar archivos manualmente:

- `GET /runs/index`: devuelve `runs_index.json`.
- `GET /runs/comparison`: devuelve `runs_comparison_latest.json`.
- `GET /runs/top?limit=5`: ranking de corridas por `operational_core_macro_f1`.

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
