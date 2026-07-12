# Objetivos

## Objetivo general

Diseñar y validar un sistema inteligente de apoyo a la toma de decisiones que recomiende el cuadrante de prueba de rendimiento más adecuado para cada endpoint, utilizando la matriz vigente de criticidad y complejidad, las configuraciones existentes, los resultados históricos de Gatling y la validación de especialistas.

## Objetivos específicos

1. Caracterizar el proceso actual de clasificación y configuración de pruebas.
2. Formalizar las dimensiones de criticidad y complejidad.
3. Formalizar los nueve cuadrantes y sus parámetros.
4. Documentar la relación entre la Tripleta y la matriz completa.
5. Construir un parser para `performance.yaml`.
6. Construir un parser para `parametricConfigurationValues.yaml`.
7. Procesar resultados Gatling globales y por endpoint.
8. Consolidar un historial normalizado de configuraciones, cuadrantes y resultados.
9. Implementar un baseline basado en la matriz y reglas expertas.
10. Diseñar un recomendador de cuadrante.
11. Recomendar mantener, aumentar, disminuir o revisar la clasificación.
12. Generar explicaciones trazables.
13. Incorporar validación humana.
14. Registrar aceptación, modificación o rechazo.
15. Comparar el sistema con el proceso manual.
16. Evaluar precisión, consistencia, productividad y utilidad.
17. Diseñar una arquitectura extensible hacia nuevas variables.
18. Evaluar una migración parcial de `performance-lib` desde Java a Python como habilitador técnico.

## Hipótesis preliminar

La combinación de una matriz formalizada, reglas expertas, resultados históricos y recomendación asistida permitirá aumentar la consistencia y reducir el esfuerzo necesario para seleccionar configuraciones de rendimiento, manteniendo la decisión final en el especialista.

## Hipótesis técnica secundaria

La migración parcial de los componentes de lectura, validación y normalización desde Java a Python facilitará la experimentación, la integración con modelos de Inteligencia Artificial y la evolución de la matriz, sin alterar el comportamiento esperado del proceso vigente.