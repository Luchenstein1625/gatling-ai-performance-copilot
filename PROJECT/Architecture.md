# Arquitectura Preliminar

## Flujo general

```text
Información del endpoint
        +
criticidad y complejidad
        +
performance.yaml
        +
parametricConfigurationValues.yaml
        |
        v
Ingesta y validación
        |
        v
Motor de matriz
        |
        +--> Cuadrante inicial
        +--> Tripleta
        +--> Apdex esperado
        +--> Throughput esperado
        +--> Ramp-up
        +--> Duración
        +--> Cantidad VU
        |
        v
Ejecución Gatling
        |
        v
Parser de resultados
        |
        v
Historial normalizado
        |
        v
Baseline y motor inteligente
        |
        +--> Mantener cuadrante
        +--> Subir cuadrante
        +--> Bajar cuadrante
        +--> Revisar manualmente
        |
        v
Explicación
        |
        v
Validación especialista
        |
        v
Registro de feedback