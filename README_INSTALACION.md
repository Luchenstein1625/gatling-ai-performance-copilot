# H10 nativo — instalación

Este paquete incorpora H10 dentro de la CLI existente y registra directamente:

```text
pde pipeline
```

## Aplicar

Puedes ejecutar el instalador desde la raíz del repositorio:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\INSTALL_H10.ps1
```

También puedes ejecutarlo estando dentro de `app`:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
..\INSTALL_H10.ps1
```

El instalador:

1. copia los archivos nuevos;
2. modifica `interfaces/cli/main.py`;
3. registra `register_pipeline_command(app, console)`;
4. reinstala el paquete editable;
5. comprueba que `pipeline` aparezca en `pde --help`.

## Verificación

```powershell
cd app
pde --help
pde pipeline --help
black --check .
ruff check .
mypy src
pytest -v
```

## Ejecución

```powershell
pde pipeline `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
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

## Archivos obligatorios generados

```text
execution_summary.json
recommendation.json
dataset.csv
pipeline_summary.json
report.html
```

Los artefactos de Machine Learning se generan solo cuando el dataset cumple las validaciones de H8.
