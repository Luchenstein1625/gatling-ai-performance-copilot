# Aplicación del H10 local PoC

## 1. Copiar los archivos

Descomprime el ZIP en la raíz del repositorio permitiendo crear archivos nuevos.

## 2. Aplicar la modificación mínima

Desde la raíz:

```powershell
python .\apply_h10_patch.py
```

El script modifica únicamente:

```text
app/src/performance_decision_engine/interfaces/cli/main.py
app/docs/development/README.md
```

En `main.py` agrega:

```python
from performance_decision_engine.interfaces.cli.pipeline import register_pipeline_command
```

y:

```python
register_pipeline_command(app, console)
```

## 3. Instalar y validar

```powershell
cd app
pip install -e ".[dev]"
black --check .
ruff check .
mypy src
pytest -v
```

## 4. Ejecutar

```powershell
pde pipeline `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output-dir examples/output/pipeline
```

Con intento de entrenamiento:

```powershell
pde pipeline `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output-dir examples/output/pipeline `
  --train
```

## 5. Revisar artefactos

```text
examples/output/pipeline/
```

Abrir:

```text
report.html
```

## 6. Git

```powershell
cd ..
git status
git add app apply_h10_patch.py
git commit -m "feat: implementar hito 10 como poc local end-to-end"
git push
```
