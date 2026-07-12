# H1 - Project Bootstrap

## Objetivo

Crear la base técnica del proyecto siguiendo una arquitectura desacoplada que permita evolucionar el motor de decisión sin depender de una herramienta específica de pruebas de rendimiento.

## Problema

El desarrollo del proyecto requería una estructura mantenible, escalable y preparada para incorporar nuevos componentes sin afectar el núcleo del dominio.

## Solución

Se implementó una arquitectura basada en Clean Architecture separando:

- Domain
- Application
- Infrastructure
- Interfaces

## Componentes implementados

- Proyecto Python
- CLI
- API
- pyproject.toml
- requirements
- pruebas unitarias
- documentación inicial

## Resultado

El proyecto puede instalarse mediante:

```powershell
pip install -e ".[dev]"
```

y verificar su funcionamiento con:

```powershell
pde doctor
```

## Estado

✅ Completado

## Próximo hito

Implementar el parser de parámetros.