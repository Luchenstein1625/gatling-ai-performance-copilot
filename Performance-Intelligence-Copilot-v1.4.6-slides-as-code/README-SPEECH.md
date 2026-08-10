# Guion de presentación — versión 1.5.0

Duración objetivo: **15 minutos** · 14 diapositivas.

| Slide | Tema | Tiempo |
|---:|---|---:|
| 1 | Portada | 0:35 |
| 2 | Contexto y evolución | 1:00 |
| 3 | Problema de negocio | 1:05 |
| 4 | Objetivo, alcance y KPI | 1:00 |
| 5 | Metodología y arquitectura | 1:05 |
| 6 | Dataset y EDA | 1:25 |
| 7 | ETL y prevención de fuga | 1:10 |
| 8 | Comparación de soluciones IA | 1:30 |
| 9 | Error y sobreajuste | 1:10 |
| 10 | Pipeline por capas | 1:10 |
| 11 | Sensibilidad y costos | 1:15 |
| 12 | Recomendación y evaluación económica | 1:15 |
| 13 | Validación y trabajos futuros | 1:00 |
| 14 | Conclusiones | 0:30 |

## Mensajes principales

### 1–5 · Problema y solución

El proyecto automatiza el análisis de resultados Gatling para apoyar la decisión sobre la configuración siguiente. La salida no reemplaza al especialista: genera una recomendación explicable y auditable. Una falla nunca provoca una reducción automática del cuadrante; pasa a `review`.

### 6 · Dataset y EDA

El input real contiene 6.445 filas y 6.444 son utilizables. La variable objetivo separa 3.781 casos `not_applies` y 2.663 `applies`. El holdout contiene 1.330 registros y no comparte ningún `Build_Id` con entrenamiento. `apdex` no es numérico y `rating` está vacío, por lo que se excluyen.

### 7 · ETL

El TXT se normaliza, valida y transforma en variables auditables. La partición se realiza por `Build_Id` para evitar fuga. No se usan como predictoras columnas posteriores que revelen directamente la etiqueta.

### 8 · Comparación IA

Se comparan baseline mayoritario, árbol de decisión, regresión logística y Random Forest. Random Forest obtiene el mejor resultado en holdout: accuracy 0,7256, F1 0,7446 y recall 0,7046 para `not_applies`. El baseline no es candidato porque predice siempre la clase mayoritaria.

### 9 · Sobreajuste

Random Forest baja de 0,8318 a 0,7256 en accuracy entre train y test. La brecha obliga a mantener la decisión humana. El resultado es suficiente para apoyo a la decisión, no para automatización autónoma.

### 10 · Cuatro capas

La primera capa estima aplicabilidad; la segunda produce `review`, `maintain` o `upgrade`; la tercera propone cuadrante y parámetros; la cuarta exige una nueva ejecución Gatling. En el holdout se generan 674 review, 383 maintain y 273 upgrade. Ningún review altera automáticamente la configuración.

### 11 · Sensibilidad y costo

El error más costoso es predecir `applies` cuando la configuración realmente no aplica. Por eso, ante falla, irregularidad o evidencia insuficiente, la política envía el caso a `review`. El cut-off definitivo debe calibrarse con costos reales del piloto.

### 13 · Validación

Las recomendaciones upgrade están en `pending_new_execution`. Para aprobarlas hay que ejecutar Gatling con la configuración propuesta y comparar errores, p95, RPS, éxitos y estado. Si falla, vuelve a review; no hay downgrade automático.

### 14 · Cierre

La POC cumple el objetivo técnico: procesa 6.444 ejecuciones, compara modelos, genera una decisión por capas y conserva control humano. Quedan pendientes la validación experimental de las configuraciones nuevas y la medición económica del piloto.
