# Instrucciones de actualización

## Archivos incluidos

```text
README.md
CHANGELOG.md
app/README.md
app/docs/development/README.md
app/docs/development/H7_DatasetGeneration.md
app/docs/development/H8_MachineLearning.md
app/docs/development/H9_Explainability.md
```

## Aplicación

Descomprime el ZIP sobre la raíz del repositorio y permite reemplazar los archivos.

```powershell
git diff -- README.md CHANGELOG.md app/README.md app/docs/development
git add README.md CHANGELOG.md app/README.md app/docs/development
git commit -m "docs: actualizar estado hasta hito 9"
git push
```

## Estado documentado

```text
H1–H9: completados
H10: pendiente
```

## Validación técnica

```powershell
cd app
black --check .
ruff check .
mypy src
pytest -v
```
