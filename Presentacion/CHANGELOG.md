# Historial de versiones

Todos los cambios relevantes de la presentación se registran en este archivo.

## [1.6.4] — 2026-08-04

- **Slide 10 · Integración en el pipeline**: nueva lámina que muestra un mockup de pipeline Azure DevOps con la recomendación del Copilot como gate antes de la ejecución de Gatling. La tarjeta del Copilot pulsa con animación CSS mientras espera la aprobación del especialista QA.

## [1.6.3] — 2026-08-04

- **Slide 10**: nota de pie corregida para separar cifras reales calculadas (3.960 casos, 4,8 UF/prueba, 19.008 UF/año, $718,5 MM) del escenario preliminar (50 %/75 %). Solo el escenario lleva la advertencia de proyección pendiente de piloto.

## [1.6.2] — 2026-08-04

- **Slide 10 · Impacto operacional**: reestructurada con cifras en UF. Tarjeta 1: base histórica anual 19.008 UF (≈ $718,5 MM). Tarjeta 2: alcance de cobertura 3.960 casos/año en 11 pipelines. Tarjeta 3: escenario preliminar 7.128 UF/año (≈ $269,4 MM) con supuestos 50 % cobertura × 75 % reducción. Sustento matemático incorporado en la nota de pie.

## [1.6.1] — 2026-08-04

- **Slide 02 · Problema de negocio**: reestructurada con cifras reales del equipo. Cuatro tarjetas: volumen operativo (3.960 casos/año · 11 pipelines), costo anual estimado (19.008 UF ≈ $718 MM/año), costo promedio por caso (4,8 UF ≈ $181 mil) y desglose de esfuerzo (ciclo completo 34,5 UF; 86 % en automatización y mantención). Sustento matemático incorporado en la narrativa.

## [1.6.0] — 2026-08-04

### Correcciones metodológicas y de datos
- **Slide 03 · KPI**: se reemplazaron los resultados de `all_features` (1,00) por los de `operational_core` (Macro-F1 0,5987 · balanced acc. 0,62 · desv. 0,1738 · mejora +0,1820 pp). Se añade nota explicando por qué `operational_core` es el resultado principal.
- **Slide 08 · Primer modelo**: la tabla cualitativa de señales fue reemplazada por la importancia Gini real del árbol entrenado (`error_rate_percent` = 0,50 · `min_response_time_ms` = 0,50), extraída de `historical_model_explanation.json`.
- **Slide 09 · Evaluación**: se añade párrafo explícito sobre el F1 de la clase review en `operational_core` (media 0,3968 · mín 0,00 · máx 0,80) con contexto vs baseline (0,00).
- **Slide 09 · Baseline**: la comparación ahora usa la misma métrica que el modelo: Macro-F1 0,4167 · balanced accuracy 0,50 · review F1 0,00.
- **Slide 09 · Etiquetas**: corregido "20 maintain" → "20 evolve" y la matriz agregada para consistencia con el nuevo esquema de validación.
- **Slide 11 · Conclusión**: texto reescrito para no afirmar "reproducción de reglas"; dice explícitamente que supera el baseline con señales operacionales y que la generalización debe validarse.

### Ajustes visuales y estructurales
- **Slide 07 · ETL**: rediseñado con layout de dos columnas: control de muestra/fuga de información a la izquierda y panel de preprocesamiento real a la derecha.
- **Slides 05 y 06**: divididas en dos láminas independientes (composición/calidad y exploración multivariable).
- **Slides 08–09**: corregida expresión "30 semillas" → "30 particiones holdout estratificadas con `StratifiedShuffleSplit`".
- **Slide 04**: notas metodológicas actualizadas con hiperparámetros reales del árbol y justificación de variantes.
- Eliminada la slide de "Validación en un caso real".
- Auditoría completa de cifras: todos los números de la presentación verificados contra los reportes de la última ejecución.

## [1.5.5] — 2026-08-03

- Se actualizó la lámina 05 para reflejar el último corte importado: 11 detectadas, 11 completas y 11 finales (11 maintain / 0 review).
- Se regeneró `graficos-lamina-6.png` con `Resultados/dataset.csv` del corte actual, mostrando tasa de error y margen p95 vs SLA por ejecución importada.
- Se explicitó en la narrativa que este corte es descriptivo y que la comparación de clases se mantiene en la corrida histórica de 28 casos.

## [1.5.4] — 2026-08-03

- Se rediseñó la lámina 03 con una estructura moderna y elegante: hero principal, tres tarjetas limpias y chips KPI compactos.
- Se eliminaron bloques visuales pesados y se mejoró la jerarquía de lectura para proyección.

## [1.5.3] — 2026-08-03

- Se rediseñó la lámina 03 para eliminar sensación de desorden: bloque principal más legible, tres tarjetas con texto breve y franja KPI en formato compacto.
- Se aumentó tamaño de tipografías y se mejoró la proporción de columnas para lectura en proyección.

## [1.5.2] — 2026-08-03

- Se corrigió un error de JSX en la lámina 03 que impedía compilar la presentación.
- Se rearmó la estructura de la lámina 03 (objetivo, alcance y KPI) para eliminar el desorden visual y mejorar legibilidad.
- Se restauró correctamente la sección de data-quality para evitar cruces de contenido entre láminas.

## [1.5.2] — 2026-08-03

- Se rehízo la lámina 03 con una estructura ejecutiva y legible: objetivo general, tres tarjetas equilibradas y franja KPI compacta.
- Se eliminaron columnas estrechas y bloques que comprimían el texto, priorizando lectura en proyección.

## [1.5.2] — 2026-08-03

- Se rediseñó nuevamente la lámina 03 para priorizar legibilidad: objetivo central más visible, tarjetas homogéneas y KPI en chips compactos.
- Se eliminó la compresión extrema de texto y se corrigió la jerarquía visual para defensa en proyección.

## [1.5.1] — 2026-08-03

- Se simplificó la lámina 03 (Objetivo, alcance y KPI) para reducir sobrecarga visual y mejorar legibilidad en defensa.
- Se compactó el texto de los tres objetivos específicos y se redujo la franja de umbrales KPI a una versión ejecutiva.
- Se ajustó el layout de la lámina a tres tarjetas compactas y bloques inferiores más livianos.

## [1.5.0] — 2026-08-03

- Se alinearon todas las láminas de evaluación a la corrida vigente con 30 semillas.
- Slide 9 ahora reporta `operational_core` (Macro-F1 0,5987; IC95 [0,5365; 0,6609]) y explicita riesgo de sobreajuste.
- Se agregó gráfico nuevo `graficos-lamina-9.png` con comparación de variantes e intervalo de confianza.
- Se actualizó el guion de defensa (`README-SPEECH.md`) y la evidencia (`DEFENSA_EVIDENCIA_RESULTADOS.md`) para consistencia numérica.

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
