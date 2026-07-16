# Desarrollo del Proyecto

Esta carpeta documenta la evolución técnica del Performance Decision Engine.

Cada hito debe registrar objetivo, diseño, componentes, ejecución, pruebas, evidencia, limitaciones y próximo paso.

## Orden de desarrollo

| Hito | Nombre | Estado |
|---|---|:---:|
| H1 | Project Bootstrap | ✅ |
| H2 | Parameter Values | ✅ |
| H3 | Performance YAML | ✅ |
| H4 | Gatling Results | ✅ |
| H5 | Normalization | ✅ |
| H6 | Decision Matrix | ✅ |
| H7 | Dataset Generation | ✅ |
| H8 | Machine Learning | ✅ |
| H9 | Explainability | ✅ |
| H10 | Integration | ⏳ |

## Estado actual

El proyecto ya puede normalizar ejecuciones, recomendar, generar datasets, importar históricos, validar y entrenar un baseline supervisado y explicar sus decisiones.

## Quality Gates

```powershell
black --check .
ruff check .
mypy src
pytest -v
```

## Próximo hito

**H10 — Integration**
