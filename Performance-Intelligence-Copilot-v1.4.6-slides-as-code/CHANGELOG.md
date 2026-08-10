# Historial de versiones

Todos los cambios relevantes de la presentación se registran en este archivo.

## [1.5.0] — 2026-08-10

- Reestructuración completa según la rúbrica `Pres3`.
- Dataset real actualizado: 6.444 ejecuciones utilizables de 6.445 filas.
- EDA con distribución `not_applies`/`applies`, calidad de variables y split por `Build_Id`.
- Comparación de baseline, árbol de decisión, regresión logística y Random Forest.
- Métricas train/test, matriz de confusión y discusión explícita del sobreajuste.
- Pipeline de cuatro capas: aplicabilidad, decisión, optimización y validación Gatling.
- Análisis del costo asimétrico de falsos `applies` y política conservadora de `review`.
- Recomendación operacional `review`/`maintain`/`upgrade`; no existe downgrade automático.
- Evaluación económica conservada como escenario preliminar sujeto a piloto.
- Trabajos futuros y estado `pending_new_execution` incorporados sin presentar la recomendación como validación real.

## [1.4.4] — 2026-08-03

- Slide 6: diccionario visual de seis variables principales y sus roles.
- Slide 7: embudo ETL y visualización explícita de nulos por columna.
- Slide 8: importancia aprendida por el árbol, regla de decisión y advertencia sobre `warning_count` como posible proxy.
- Se conservan los gráficos históricos reales y la evaluación repetida con diez semillas.

## [1.4.3] — 2026-08-02

- Se documentó el holdout estratificado repetido con 10 semillas y particiones de 21/7 casos.
- Se incorporó Macro-F1 medio 1,0000, desviación estándar 0,0000 y rango 1,0000–1,0000.
- Se explicitó la regla aprendida mediante `assertions_failed` y el riesgo de `warning_count` como variable proxy en la ablación.
- Se reforzó que la evaluación mide fidelidad respecto del motor H6 y no demuestra generalización operacional.

## [1.2.0] — 2026-08-02

## [1.3.0] - 2026-08-02

### Evaluación económica preliminar según rúbrica Pres2

- Se incorporó en la descripción del problema la base histórica de 7.003 atenciones y $1.569 MM anuales.
- Se calculó un costo promedio ponderado referencial de aproximadamente $224 mil por atención.
- Se agregó al impacto operacional el alcance de 144 atenciones anuales y un costo abordable aproximado de $32,3 MM.
- Se incluyó un escenario preliminar de 50 % de cobertura y 75 % de reducción, equivalente a un beneficio bruto potencial de $12,1 MM anuales.
- Las cifras se presentan como estimaciones referenciales, no como ahorro comprobado.

## [1.2.0] - 2026-08-02

### Refuerzo según rúbrica Pres2, sin evaluación económica

- Se hizo explícita la relación observada entre incumplimientos y la decisión `review`.
- Se separaron las variables utilizadas de `p90`, excluida por ausencia total de datos.
- Se aclaró que la muestra de 28 ejecuciones no permite afirmar correlaciones robustas ni generalización.
- Se reforzó la evaluación del árbol con diez semillas estratificadas, comparación contra baseline y ablación sin `assertions`.
- Se explicitó que el resultado estable no constituye significancia estadística por el tamaño de la muestra.
- No se agregaron costos, ahorros monetarios ni supuestos económicos.

## [1.1.0] — 2026-08-02

### Ajustes según retroalimentación del profesor

- Se compactaron implementación y evolución en una sola lámina, reduciendo la presentación de 13 a 12 diapositivas sin eliminar evidencia técnica.
- Se agregó una definición simple de las pruebas de rendimiento y se identificó explícitamente el cuello de botella.
- Se preservaron y destacaron los rangos reales: 3–48 horas de desarrollo y análisis, 1–35 horas de aprobación QA y 12 tareas mensuales.
- Se aclaró la comparación: el desarrollo y análisis baja a minutos; la aprobación humana se mantiene asistida y debe medirse en operación.
- Se incorporaron retrabajos, retesting, correcciones y atrasos indirectos al negocio.
- Se mantuvo un único diagrama de solución, desde las fuentes hasta la recomendación.
- Se eliminaron referencias internas H6/H8 y nombres de código innecesarios para mejorar la claridad narrativa.

## [1.0.0] — 2026-08-02

Primera versión formal de la presentación como código, basada en la versión vigente de 13 diapositivas.

### Incluye

- Problema cuantificado: desarrollo de 3 a 48 horas, aprobación de 1 a 35 horas y 12 tareas mensuales.
- Comparación operacional visible: hasta 48 horas frente a minutos.
- Objetivo, alcance, entregables y KPI.
- Metodología y arquitectura en un flujo único.
- Descripción y visualización de las 28 ejecuciones utilizadas.
- Variable objetivo y variables predictoras identificadas.
- ETL, preprocesamiento, nulos, columnas excluidas y filas finales.
- Ingeniería de atributos explícita.
- Primer y único tipo de modelo entrenado: árbol de decisión.
- Comparación con baseline y reglas expertas de recomendación.
- Evaluación, caso real, controles de sobreajuste y limitaciones.
- Impacto esperado, esfuerzo de implementación y evolución hacia un YAML propuesto.

### Versionado

- Se agregó `presentation.config.ts` como fuente única de la versión.
- La versión aparece en el pie de cada diapositiva.
- Se documentó el flujo para commits y etiquetas de Git.
# Corrección metodológica de evaluación

- Se corrigió el Macro-F1 del baseline mayoritario de 0,7143 a 0,4167; 0,7143 queda identificado como accuracy.
- Se explicitó el protocolo verificable: 28 casos, distribución 20/8, diez particiones estratificadas, Macro-F1, balanced accuracy y ablación sin assertions.
- Se aclaró que `recommendation_action` proviene del motor determinístico H6 y que el árbol evalúa fidelidad respecto de esas reglas.
- Se reservó la validación con etiquetas humanas independientes y casos nuevos como trabajo posterior.
