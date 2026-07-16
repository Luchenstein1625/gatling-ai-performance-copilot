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
| H10 | Local End-to-End Integration PoC | ✅ |

## Estado actual

El proyecto puede:

- normalizar ejecuciones;
- generar recomendaciones determinísticas;
- construir datasets;
- importar históricos;
- validar y entrenar un baseline supervisado;
- explicar decisiones y modelos;
- ejecutar el flujo completo mediante `pde pipeline`;
- generar un resumen JSON y un reporte HTML local.

## Quality Gates

```powershell
black --check .
ruff check .
mypy src
pytest -v
```

## Estado del roadmap

Los diez hitos técnicos planificados se encuentran implementados para la PoC local.

Las conexiones con plataformas corporativas quedan como evolución posterior y deberán realizarse mediante adaptadores.
