# Guía de Contribución

## Flujo recomendado

1. Actualizar `main`.
2. Crear rama.
3. Implementar una unidad pequeña.
4. Agregar pruebas.
5. Ejecutar calidad.
6. Crear Pull Request.

```bash
git checkout main
git pull
git checkout -b feature/nombre-corto
```

## Convenciones

- código y nombres técnicos en inglés;
- documentación de negocio en español;
- funciones pequeñas;
- type hints obligatorios;
- no mezclar parsing con reglas de negocio;
- no inventar datos faltantes;
- toda recomendación debe conservar evidencia.

## Antes de realizar commit

```bash
pytest
ruff check .
black --check .
mypy src
```

## Commits

Ejemplos:

```text
feat(parser): add performance yaml parser
test(domain): cover quadrant matrix
docs(app): explain local execution
fix(storage): preserve UTF-8 output
```
