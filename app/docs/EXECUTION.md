# Ejecución

## Instalar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Validar

```powershell
pde doctor
pytest
```

## Normalizar ejemplo

```powershell
pde normalize `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output examples/output/execution_summary.json
```
