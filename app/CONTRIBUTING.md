# Contribución

## Convenciones

- código técnico en inglés;
- documentación funcional en español;
- type hints obligatorios;
- pruebas para cada comportamiento;
- el dominio no depende de frameworks;
- los parsers no toman decisiones;
- los valores desconocidos se conservan como `None`;
- ninguna recomendación puede inventar métricas.

## Antes de un commit

```powershell
pytest
ruff check .
black --check .
mypy src
```

## Ramas

```text
feature/*
fix/*
docs/*
refactor/*
experiment/*
```
