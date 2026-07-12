# Arquitectura

## Regla de dependencias

```text
interfaces -> application -> domain
infrastructure -> application/domain
domain -> nada externo
```

## Dominio

Contiene entidades y reglas puras.

## Aplicación

Orquesta casos de uso y trabaja contra puertos.

## Infraestructura

Conoce archivos, YAML, JSON y persistencia.

## Interfaces

Expone CLI y API.
