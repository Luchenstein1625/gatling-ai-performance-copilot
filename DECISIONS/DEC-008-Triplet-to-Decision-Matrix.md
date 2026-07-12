# DEC-008 — Evolución desde Tripleta hacia Matriz de Decisión

## Fecha

2026-07-12

## Estado

Propuesta pendiente de validación académica y experta.

## Contexto

Inicialmente el Capstone consideraba recomendar una Tripleta formada por:

- concurrencia;
- iteraciones;
- tiempo de respuesta.

Posteriormente se identificó una matriz vigente que clasifica los endpoints mediante criticidad y complejidad, generando nueve cuadrantes.

Cada cuadrante incorpora más variables que la Tripleta:

- concurrencia;
- iteraciones;
- tiempo de respuesta;
- Apdex;
- throughput;
- ramp-up;
- duración;
- cantidad VU.

## Decisión

1. Mantener la Tripleta como concepto operativo existente.
2. Adoptar la matriz de nueve cuadrantes como representación principal del dominio.
3. Definir el objetivo del MVP como recomendación de cuadrante.
4. Permitir que la arquitectura evolucione hacia una matriz con nuevas variables.
5. Mantener validación humana.
6. Utilizar resultados históricos como evidencia.
7. Tratar la migración parcial de Java a Python como habilitador técnico.
8. No considerar la migración como el aporte principal de IA.
9. Validar formalmente los conceptos de concurrencia, cantidad VU e iteraciones antes de implementarlos.
10. Comparar la solución con la matriz vigente y con especialistas.

## Consecuencias

- el problema queda mejor alineado con el proceso real;
- el alcance de IA se concentra en la recomendación;
- la Tripleta no se elimina;
- el sistema mantiene compatibilidad conceptual con el proceso actual;
- la arquitectura puede incorporar más variables;
- se requieren datos históricos y etiquetas expertas;
- se deben resolver ambigüedades antes de construir el motor definitivo.