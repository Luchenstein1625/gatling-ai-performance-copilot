# Problema de Negocio

## Contexto actual

La configuración de pruebas de rendimiento se realiza mediante una matriz de decisión compuesta por nueve cuadrantes.

Cada cuadrante surge de combinar:

- criticidad del endpoint o servicio;
- complejidad del endpoint o servicio.

La clasificación determina valores asociados a:

- concurrencia;
- iteraciones;
- tiempo de respuesta esperado;
- Apdex;
- throughput;
- ramp-up;
- duración;
- cantidad de usuarios virtuales.

La configuración es declarada en archivos como `performance.yaml` y complementada con valores maestros administrados por QA Infraestructura.

La biblioteca Java `performance-lib` interpreta estos archivos y participa en la preparación o ejecución de la prueba Gatling.

## Problema principal

Aunque existe una matriz definida, la clasificación inicial de criticidad y complejidad continúa dependiendo del conocimiento del equipo o especialista.

Además, los resultados históricos de Gatling no se utilizan de forma sistemática para determinar si:

- el cuadrante seleccionado fue apropiado;
- el endpoint debería cambiar de cuadrante;
- la configuración fue demasiado exigente;
- la configuración fue insuficiente;
- existen patrones similares en otros endpoints;
- la decisión del especialista se mantiene consistente en el tiempo.

## Consecuencias

- variabilidad entre equipos;
- dependencia del conocimiento experto;
- criterios difíciles de reproducir;
- baja reutilización del historial;
- configuraciones potencialmente subdimensionadas;
- configuraciones potencialmente sobredimensionadas;
- análisis manual de resultados;
- trazabilidad limitada;
- dificultad para explicar la selección;
- dificultad para evolucionar la matriz de manera controlada.

## Oportunidad

Construir un sistema inteligente que formalice el proceso actual, consolide configuraciones y resultados, recomiende un cuadrante y permita que el especialista valide la recomendación.

## Pregunta de investigación preliminar

¿En qué medida un sistema inteligente, basado en la matriz vigente, reglas expertas, resultados históricos de Gatling y validación humana, puede mejorar la consistencia y reducir el esfuerzo requerido para seleccionar el cuadrante de prueba de rendimiento de un endpoint?

## Preguntas complementarias

1. ¿Es posible predecir el cuadrante a partir de características funcionales y técnicas?
2. ¿El historial de Gatling permite recomendar mantener, aumentar o disminuir un cuadrante?
3. ¿Una recomendación explicable alcanza una aceptación comparable al criterio experto?
4. ¿La solución reduce el tiempo de preparación y análisis?
5. ¿Una matriz ampliada produce mejores recomendaciones que la Tripleta por sí sola?