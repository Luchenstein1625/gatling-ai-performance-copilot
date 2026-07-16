# H10 sin parches

Este paquete no utiliza archivos `.patch`, `git apply` ni scripts de instalación.

## Aplicación

Descomprime el ZIP directamente sobre la raíz del repositorio:

```text
gatling-ai-performance-copilot/
├── README.md
├── CHANGELOG.md
└── app/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    ├── tests/
    └── docs/
```

Permite reemplazar los archivos existentes.

## Qué se modifica

No se modifica `interfaces/cli/main.py`.

El archivo completo `app/pyproject.toml` cambia el punto de entrada:

```toml
[project.scripts]
pde = "performance_decision_engine.interfaces.cli.h10_main:app"
```

El nuevo archivo:

```text
app/src/performance_decision_engine/interfaces/cli/h10_main.py
```

importa la CLI actual y registra el comando H10:

```python
from performance_decision_engine.interfaces.cli.main import app, console
from performance_decision_engine.interfaces.cli.pipeline import register_pipeline_command

register_pipeline_command(app, console)
```

## Reinstalar

Desde `app`:

```powershell
pip install -e ".[dev]"
```

## Verificar

```powershell
pde --help
pde pipeline --help
```

## Ejecutar

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

## Validar

```powershell
black --check .
ruff check .
mypy src
pytest -v
```

## Revertir

Como todos los cambios son archivos completos, puedes volver a `main` con:

```powershell
git reset --hard origin/main
git clean -fd
```
