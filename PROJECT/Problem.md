# Problema de Negocio

## Situación actual
Cada endpoint se configura mediante una matriz que combina criticidad y complejidad y define concurrencia, iteraciones, tiempo de respuesta, Apdex, throughput, ramp-up, duración y cantidad VU.

## Problema principal
La selección del cuadrante continúa dependiendo del criterio experto y no aprovecha sistemáticamente el historial Gatling.

## Consecuencias
- variabilidad entre equipos;
- dependencia del conocimiento experto;
- riesgo de subdimensionamiento o sobredimensionamiento;
- análisis manual;
- baja trazabilidad;
- poca reutilización del historial.

## Pregunta de investigación
¿En qué medida un sistema inteligente basado en la matriz vigente, reglas expertas, historial Gatling y validación humana puede mejorar la consistencia y reducir el esfuerzo para seleccionar el cuadrante de un endpoint?
