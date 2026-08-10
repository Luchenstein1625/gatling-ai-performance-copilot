# Speech de presentación — 15:00 minutos

Versión 1.4.1 · Agosto 2026 · 13 láminas · tiempo total objetivo: **900 segundos**.

> El tiempo indicado incluye las pausas breves marcadas. Practicar una vez con cronómetro y respetar el cierre de cada bloque permite terminar en 15:00, sin considerar preguntas.

| Slide | Tema | Tiempo | Acumulado |
|---:|---|---:|---:|
| 1 | Portada | 0:45 | 0:45 |
| 2 | Negocio bancario y cambio de enfoque | 1:20 | 2:05 |
| 3 | Problema de negocio | 1:15 | 3:20 |
| 4 | Objetivo, alcance y KPI | 1:10 | 4:30 |
| 5 | Metodología y arquitectura | 1:15 | 5:45 |
| 6 | Datos y EDA | 1:20 | 7:05 |
| 7 | ETL e ingeniería de atributos | 1:25 | 8:30 |
| 8 | Primer modelo entrenado | 1:20 | 9:50 |
| 9 | Evaluación del modelo | 1:15 | 11:05 |
| 10 | Validación en un caso real | 1:00 | 12:05 |
| 11 | Impacto operacional y económico | 1:15 | 13:20 |
| 12 | Implementación y evolución | 0:55 | 14:15 |
| 13 | Conclusiones | 0:45 | 15:00 |

## Slide 1 — Portada · 0:45

“Buenas tardes. Somos el Grupo 8, integrado por Luis Araya, Rodrigo González y Hernán Medina. Nuestro proyecto se llama Performance Intelligence Copilot. Es una prueba de concepto que combina reglas expertas y aprendizaje automático explicable para apoyar decisiones en pruebas de rendimiento. La idea central no es reemplazar al especialista ni ejecutar cambios de manera autónoma. Buscamos ordenar la evidencia técnica, analizarla de forma reproducible y proponer una siguiente acción que siempre debe ser validada por una persona. Primero explicaremos el contexto del negocio, luego el problema, la solución construida, los datos, el modelo y finalmente su impacto esperado.”

## Slide 2 — Negocio bancario y cambio de enfoque · 1:20

“En un banco, personas y empresas utilizan canales digitales para acceder a productos, operaciones y servicios integrados. Esos canales dependen de componentes tecnológicos que deben responder de manera continua y estable. Las pruebas de rendimiento son una capacidad habilitante porque permiten medir tiempos de respuesta, errores y capacidad antes de liberar cambios.

Nuestro planteamiento inicial estaba orientado a predecir capacidad e infraestructura cloud. Al revisar la evidencia disponible, concluimos que ese alcance era más amplio que lo que realmente podíamos demostrar. Por eso cambiamos el enfoque hacia el problema que sí observamos y para el cual sí contamos con datos: analizar pruebas Gatling.

La solución actual integra configuración, métricas e historial para entregar una recomendación explicable. Este cambio es importante porque el proyecto pasa de una proyección difícil de validar a un flujo respaldado por archivos y resultados reales. Con ese contexto llegamos al problema concreto que veremos a continuación.”

## Slide 3 — Problema de negocio · 1:15

“El cuello de botella no está solamente en ejecutar una prueba. Está en preparar los insumos, interpretar los resultados y acordar la siguiente decisión. Según el levantamiento utilizado en el proyecto, el desarrollo de la prueba puede tomar entre 3 y 48 horas, mientras que la revisión y aprobación de QA puede requerir entre 1 y 35 horas adicionales. El tiempo específico dedicado a la preparación analítica todavía no tiene una línea base independiente y se medirá en el piloto.

Además, se consideran aproximadamente 12 atenciones mensuales asociadas a este trabajo. La base histórica informada registra 7.003 atenciones anuales del servicio, con un costo total de 1.569 millones de pesos y un promedio ponderado cercano a 224 mil pesos por atención.

No afirmamos que todo ese costo pueda eliminarse. El punto es que existe una oportunidad concreta de reducir el tiempo usado en consolidar evidencia y producir una recomendación técnica trazable antes de aprobar la siguiente prueba.”

## Slide 4 — Objetivo, alcance y KPI · 1:10

“El objetivo es automatizar el análisis de configuraciones, resultados e historial para generar en minutos una recomendación explicable sobre la siguiente prueba de estrés.

Las entradas son archivos YAML, resultados JSON e historial comparable. La salida combina una recomendación con su explicación. Para evaluar el modelo usamos Macro-F1 y balanced accuracy, porque las clases no están equilibradas. Desde el punto de vista operativo, primero mediremos la línea base de preparación analítica y generación de la recomendación; la meta es llevar esa etapa a minutos, seguida siempre por validación humana.

El alcance de la prueba de concepto termina en tres recomendaciones: mantener, revisar o evaluar una evolución controlada. La solución no modifica configuraciones ni ejecuta pruebas automáticamente. Ese límite conserva el control del especialista y evita presentar como implementada una automatización que aún corresponde a una etapa futura.”

## Slide 5 — Metodología y arquitectura · 1:15

“El flujo comienza con tres grupos de evidencia: configuración, métricas e historial. Luego normalizamos y etiquetamos los datos para llevar fuentes distintas a una representación común.

La capa de inteligencia combina reglas expertas, un árbol de decisión y evaluación histórica. Las reglas conservan criterios técnicos de seguridad; el modelo aprende de casos etiquetados; y el historial ayuda a comparar la ejecución actual con antecedentes equivalentes. La salida implementada es una recomendación explicable, acompañada por la evidencia que la sustenta.

En la lámina distinguimos explícitamente lo que existe en la prueba de concepto de lo que corresponde a evolución. La API de recomendaciones y una interfaz de aprobación son objetivos posteriores. Esta separación hace que la arquitectura sea defendible: hoy podemos ejecutar el pipeline y producir artefactos trazables, pero la integración productiva todavía requiere controles, persistencia y experiencia de usuario.”

## Slide 6 — Datos y EDA · 1:20

“Partimos de 59 ejecuciones históricas detectadas. Veintinueve tenían la estructura completa y una se excluyó porque no permitía construir un registro comparable. La muestra final quedó en 28 ejecuciones: 20 etiquetadas como maintain y 8 como review, equivalentes a 71,4 y 28,6 por ciento.

El primer hallazgo del análisis exploratorio fue, por lo tanto, el desbalance de clases. Si hubiéramos usado solamente exactitud, el resultado podía favorecer la clase mayoritaria y ocultar errores en review. Por eso elegimos Macro-F1 y balanced accuracy. También evaluamos carga y concurrencia, TPS, volumen de solicitudes e historial comparable; el árbol les asignó importancia cero, por lo que no se ocultaron sino que se reportan como variables candidatas sin señal en esta muestra.

El segundo hallazgo fue de calidad de datos: p90 estaba nula en las 28 ejecuciones. Esa columna fue excluida. Como no disponemos aquí de los valores individuales para demostrar relaciones predictivas, esta lámina describe composición y calidad; cualquier asociación debe interpretarse como exploratoria. Evolve no se entrenó porque no existen casos reales etiquetados para esa clase.”

## Slide 7 — ETL e ingeniería de atributos · 1:25

“El embudo del dataset comienza con 59 ejecuciones históricas detectadas. De ellas, 29 contenían los artefactos requeridos y formaron un dataset inicial de 29 filas y 27 columnas. Durante la limpieza se validaron esquemas, tipos, archivos obligatorios, duplicados y ejecuciones abortadas.

Se excluyó una ejecución abortada y no se encontraron duplicados. También se eliminó la columna p90 porque tenía 28 de 28 valores nulos. El dataset final quedó en 28 registros y 26 variables disponibles.

No eliminamos filas por outliers: el porcentaje removido fue cero. En pruebas de rendimiento, un valor extremo puede representar una degradación real y no simplemente ruido estadístico, por lo que decidimos conservarlo como evidencia.

Finalmente se derivaron atributos con sentido técnico: cumplimiento de SLA, assertions fallidas, margen respecto del SLA e historial comparable. Así, el pipeline no solo limpia datos; convierte los archivos originales en variables auditables y relacionadas con la decisión.”

## Slide 8 — Primer modelo entrenado · 1:20

“El único modelo entrenado fue un árbol de decisión. Lo comparamos con dos referencias: una respuesta que siempre elige la opción más frecuente y las reglas técnicas que generan la recomendación original.

La lámina de selección muestra el panorama completo de señales evaluadas: carga y concurrencia, TPS, volumen, tasa de error, p95 y margen SLA, criterios derivados e historial comparable. En esta muestra, carga, TPS, volumen e historial no agregaron separación al árbol, pero no afirmamos que sean irrelevantes en otros datos. El hallazgo es una posible dependencia entre las etiquetas de H6 y variables derivadas del mismo motor, especialmente assertions_failed y warning_count.

El baseline mayoritario siempre predice maintain. Con 20 maintain y 8 review obtiene una accuracy de 0,7143, pero su Macro-F1 es 0,4167, porque no reconoce casos review. El árbol obtuvo Macro-F1 1,0000 en la muestra evaluada. Este valor se informa como resultado observado, no como garantía. Hoy el árbol aporta auditabilidad; su valor predictivo adicional deberá demostrarse con más fuentes, etiquetas expertas independientes y casos que H6 no resuelva por sí solo.

Se realizaron diez holdouts estratificados con semillas diferentes. En cada repetición se utilizaron 21 casos para entrenamiento y 7 para prueba. El árbol aprendió una única separación: cero assertions fallidas conduce a maintain y una o más conduce a review. La ablación retiró las variables de assertions, pero conservó warning_count, que también separa perfectamente las clases y puede actuar como proxy de la misma regla. Como las etiquetas provienen del motor H6, el resultado mide fidelidad respecto de ese motor, no superioridad frente al criterio experto ni generalización operacional.”

## Slide 9 — Evaluación del modelo · 1:15

“La conclusión principal no es que el modelo sea perfecto. La evaluación mide fidelidad a las etiquetas de H6 dentro de una muestra pequeña. El Macro-F1 observado fue 1,0000 frente a 0,4167 del baseline mayoritario, pero la comparación ocurre solamente sobre 28 ejecuciones, distribuidas en 20 maintain y 8 review.

El comportamiento se mantuvo en las diez evaluaciones con semillas diferentes y separación estratificada. El Macro-F1 promedio fue 1,0000, con desviación estándar 0,0000, mínimo 1,0000 y máximo 1,0000. Esta ausencia de dispersión describe solamente la muestra disponible. En esta etapa el árbol converge con la regla experta porque el dataset es pequeño y comparte una sola fuente de verdad. El valor del ML crecerá cuando el histórico incorpore etiquetas expertas independientes y señales que las reglas actuales no capturen. La ablación sin assertions todavía conservó warning_count, así que no permite afirmar independencia respecto de H6.

La recomendación final —mantener o revisar— fue generada por un motor de reglas basado en criterios técnicos auditables. El resultado perfecto no significa que el modelo esté listo para producción: las variables contienen las señales usadas en esa decisión. Por eso lo interpretamos como evidencia de que el árbol puede reproducir el comportamiento del motor sobre esta muestra, no como prueba de generalización.

El artefacto experimental disponible no conserva el detalle de cada partición más allá de esos resultados agregados. Después de esta presentación, la siguiente evaluación incorporará el registro completo por semilla, nuevas ejecuciones y decisiones revisadas por especialistas.”

## Slide 10 — Validación en un caso real · 1:00

“En este caso la ejecución actual pertenece al cuadrante 5 y presenta assertions fallidas. Las reglas expertas recomiendan review. El árbol de decisión también entrega review, por lo que existe concordancia entre ambos mecanismos.

La evaluación histórica mantiene esa misma salida y bloquea evolve. Este comportamiento refleja un principio de seguridad del proyecto: una falla actual prevalece sobre un buen historial. Aunque ejecuciones anteriores hayan sido estables, el sistema no debe sugerir aumentar la carga si la evidencia presente muestra incumplimientos.

La salida final es revisar la configuración antes de continuar, junto con una explicación trazable de las señales que activaron esa recomendación. Este caso muestra cómo reglas, modelo e historial se integran sin quitar la decisión final al especialista.”

## Slide 11 — Impacto operacional y económico · 1:15

“En el escenario actual, el desarrollo de la prueba puede requerir entre 3 y 48 horas, seguido por una revisión de QA de 1 a 35 horas. El tiempo específico de preparación analítica todavía debe medirse por separado. Cuando existen correcciones o reejecuciones, el ciclo puede extenderse nuevamente.

Con el Copilot, la preparación analítica y la recomendación se generan en minutos, mientras que la validación humana se mantiene. Para estimar el impacto utilizamos la base de 1.569 millones de pesos dividida por 7.003 atenciones, que entrega un promedio ponderado cercano a 224 mil pesos.

Las 144 atenciones anuales provienen de 12 atenciones mensuales multiplicadas por 12 meses. El 50 por ciento representa un supuesto de cobertura inicial y el 75 por ciento una meta preliminar de reducción del esfuerzo abordado. Con esos supuestos, el beneficio bruto potencial sería cercano a 12,1 millones al año. Es una estimación referencial: solo será ahorro efectivo si un piloto demuestra menor tiempo o menor costo facturado.”

## Slide 12 — Implementación y evolución · 0:55

“La prueba de concepto ya demuestra un pipeline reproducible desde los archivos de entrada hasta una recomendación explicable. Las entradas reales son YAML y resultados Gatling; las salidas son maintain, review o evolve; y la evidencia incluye las reglas activadas y su explicación.

Para evolucionar a una capacidad productiva se requiere integrar las fuentes, persistir ejecuciones y modelos, exponer una API y una interfaz de aprobación, y finalmente incorporar versionado, auditoría y reversión. La validación humana se mantiene como control central.

El próximo paso defendible no es automatizar todo de inmediato, sino ejecutar un piloto y medir dos resultados antes y después: el tiempo de análisis y la cantidad de reejecuciones.”

## Slide 13 — Conclusiones · 0:45

“Como conclusión, la principal contribución es una capa de decisión reproducible sobre evidencia que ya existe, pero que estaba dispersa. El proyecto normaliza los datos, combina reglas con un modelo explicable y entrega una recomendación revisable por especialistas.

Los siguientes pasos son validar las recomendaciones con expertos, ampliar el histórico con nuevos casos etiquetados y medir el efecto operacional en un piloto. Con esto podremos comprobar la generalización del modelo y la reducción real de tiempo y retrabajo.

En síntesis, pasamos de evidencia dispersa a una recomendación explicable, trazable y bajo control humano. Muchas gracias. Quedamos atentos a sus preguntas.”

## Comprobación del tiempo

`45 + 80 + 75 + 70 + 75 + 80 + 85 + 80 + 75 + 60 + 75 + 55 + 45 = 900 segundos = 15:00 minutos.`
