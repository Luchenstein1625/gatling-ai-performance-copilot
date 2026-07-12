# Development Guide

## Requisitos

Antes de finalizar un hito siempre ejecutar:

ruff check .

mypy src

pytest -v

## Estándares

- Python 3.11+
- Ruff
- MyPy
- Pytest
- Clean Architecture

## No modificar

- Domain
- Application

salvo que el hito lo requiera explícitamente.

## Commits

Cada hito debe quedar en un commit independiente.