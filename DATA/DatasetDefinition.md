# Definición del Dataset

## Unidad de análisis
Una fila representa una ejecución de un endpoint.

## Campos mínimos
- microservicio;
- endpoint;
- fecha;
- versión;
- ambiente;
- criticidad;
- complejidad;
- cuadrante;
- configuración;
- requests;
- OK;
- KO;
- p95;
- p99;
- throughput;
- assertions;
- decisión experta.

Los valores desconocidos deben ser `null` o `unknown`.
