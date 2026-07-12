# H2 - Parameter Values

## Objetivo

Implementar el lector de parámetros definido por QA Infraestructura.

## Entrada

parametricConfigurationValues.yaml

## Responsabilidad

Transformar niveles semánticos en valores numéricos.

Ejemplo:

```
high
```

↓

```
60
```

## Clases implementadas

- ParameterValues
- ParameterValuesDocument

## Funcionalidades

- Resolver concurrencia
- Resolver iteraciones
- Resolver tiempo de respuesta
- Validar estructura YAML
- Manejo de errores

## Pruebas

```powershell
pytest tests/test_parameter_values.py -v
```

## Resultado esperado

```
4 passed
```

## Evidencia

Archivo:

```
parameter_values.py
```

Pruebas:

```
test_parameter_values.py
```

## Estado

✅ Completado

## Próximo hito

Parser de performance.yaml