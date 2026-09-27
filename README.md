# Gatling AI Performance Copilot

Proyecto Capstone del Magíster en Inteligencia Artificial de la Universidad Adolfo Ibáñez.

**Autores:** Luis Araya, Rodrigo González y Hernán Medina.

## Resumen

Gatling AI Performance Copilot transforma resultados históricos de pruebas de rendimiento en una recomendación técnica explicable. La solución:

- normaliza evidencia Gatling;
- determina si una configuración `applies` o `not_applies`;
- traduce la clasificación en `review`, `maintain` o `upgrade`;
- propone parámetros de forma controlada;
- exige aprobación humana y una nueva ejecución Gatling antes de validar un cambio.

La POC no modifica infraestructura ni ejecuta cambios autónomos.

## Problema y decisión apoyada

El proceso actual requiere consolidar archivos, revisar errores y métricas, comparar antecedentes y justificar la siguiente acción. El proyecto apoya esta decisión:

| Salida | Acción operacional |
|---|---|
| `review` | Conservar la configuración y solicitar revisión especializada. |
| `maintain` | Mantener la configuración vigente. |
| `upgrade` | Proponer un aumento controlado de un nivel y validarlo con otra ejecución. |

Ante fallas, evidencia insuficiente o incertidumbre, `review` tiene prioridad.

## Dataset vigente

La evaluación Pres3 utiliza [`datasaet/resultadoPruebasGatling.txt`](datasaet/resultadoPruebasGatling.txt), un archivo histórico de ancho fijo.

| Elemento | Resultado |
|---|---:|
| Filas de origen | 6.445 |
| Registros utilizables | 6.444 |
| `not_applies` | 3.781 (58,7 %) |
| `applies` | 2.663 (41,3 %) |
| Entrenamiento | 5.114 registros, 408 `Build_Id` |
| Holdout | 1.330 registros, 136 `Build_Id` |
| `Build_Id` compartidos entre train y test | 0 |

La unidad de análisis es un registro histórico. La partición se realiza por `Build_Id` para evitar que registros relacionados aparezcan simultáneamente en entrenamiento y prueba.

## Variables y prevención de fuga

Los modelos usan información disponible antes de emitir la decisión, incluyendo configuración, componente, método y niveles operacionales de concurrencia, iteraciones y tiempo de respuesta.

Las métricas posteriores que revelarían directamente la etiqueta se excluyen de los predictores. RPS, p95 y errores se conservan para análisis y validación, no como entradas que permitan memorizar el resultado.

Las etiquetas se derivan de evidencia auditable de ejecución; todavía no corresponden a decisiones independientes asignadas por especialistas. Esta limitación debe mantenerse explícita al interpretar las métricas.

## Comparación de modelos

Se comparan tres soluciones de clasificación y un baseline mayoritario:

| Modelo | Accuracy test | F1 `not_applies` | Recall `not_applies` |
|---|---:|---:|---:|
| Baseline mayoritario | 0,5677 | 0,7242* | 1,0000* |
| Árbol de decisión | 0,6579 | 0,6486 | 0,5563 |
| Regresión logística | 0,6895 | 0,7165 | 0,6914 |
| **Random Forest** | **0,7308** | **0,7489** | **0,7073** |

\* El baseline predice siempre `not_applies`: no identifica ningún caso `applies` y no participa en la selección.

Random Forest se selecciona por el mayor F1 de `not_applies`; el recall se utiliza para desempatar.

## Sobreajuste y validación agrupada

Random Forest presenta una brecha entre entrenamiento y holdout, por lo que su uso se limita a apoyo de una revisión humana.

La validación `GroupKFold` de cinco particiones, agrupada por `Build_Id`, produjo:

| Métrica | Media | Mínimo | Máximo |
|---|---:|---:|---:|
| F1 `not_applies` | 0,8049 | 0,7682 | 0,8363 |
| Recall `not_applies` | 0,7779 | 0,7274 | 0,8285 |
| Accuracy | 0,7793 | 0,7564 | 0,8261 |

Estas cifras no demuestran generalización fuera del histórico ni sustituyen una validación experta independiente.

## Sensibilidad y costo del error

El análisis evalúa 17 cut-offs entre 0,10 y 0,90. Los costos relativos son supuestos configurables:

- falso `applies`: 10 unidades;
- falso `not_applies`: 2 unidades;
- revisión manual: 1 unidad.

No representan pesos del modelo ni costos monetarios demostrados.

El cut-off seleccionado es **0,35**:

| Resultado en holdout | Valor |
|---|---:|
| Recall `not_applies` | 0,8808 |
| Precision `not_applies` | 0,7430 |
| F1 `not_applies` | 0,8061 |
| Falsos `applies` | 90 |
| Falsos `not_applies` | 230 |
| Revisiones manuales | 895 |
| Costo esperado | 2.255 unidades |

La salida operacional resultante contiene 895 casos `review`, 217 `maintain` y 218 candidatos `upgrade`.

## Pipeline por capas

1. **Aplicabilidad:** clasifica `applies` o `not_applies`.
2. **Decisión:** traduce la evidencia en `review`, `maintain` o `upgrade`.
3. **Optimización:** aprende perfiles robustos de casos exitosos y propone concurrencia, iteraciones y tiempo de respuesta.
4. **Validación:** exige una nueva ejecución Gatling y compara errores, p95, RPS, éxitos y estado.

Una propuesta `upgrade` permanece en `pending_new_execution` hasta disponer de esa nueva prueba. Si la ejecución falla o presenta regresión, vuelve a `review`.

## Ejecución reproducible

Desde `app`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"

pde evaluate-complete `
  --source "..\datasaet\resultadoPruebasGatling.txt" `
  --output-dir "..\Resultados\complete_feedback"
```

Resultado esperado:

```text
Rows evaluated: 6444
Selected model: random_forest
Future online validation: pending new Gatling execution
```

## Evidencia versionada

La carpeta [`Resultados/complete_feedback`](Resultados/complete_feedback) contiene:

- `complete_pipeline_evaluation.json`;
- `threshold_cost_analysis.csv`;
- `segment_metrics.csv`;
- `layered_recommendations.csv`;
- `decision_tree.dot`;
- `decision_tree_rules.txt`;
- `layer1_applicability_model.joblib`.

El JSON es la fuente principal de métricas. Los CSV permiten auditar sensibilidad, costos, segmentos y recomendaciones.

## Verificación

Desde `app`:

```powershell
pytest -v
ruff check .
black --check .
python scripts/verify_pres3_evidence.py
```

El chequeo estático con `mypy src` aún reporta deuda de tipado en el evaluador histórico
y en algunos comandos experimentales. No afecta las 100 pruebas automatizadas, pero se
mantiene como mejora técnica pendiente y no se declara como control aprobado.

## Evaluación económica

El escenario preliminar considera:

- 12 atenciones mensuales;
- 144 atenciones anuales;
- costo promedio ponderado cercano a $224.000 CLP por atención;
- cobertura inicial supuesta de 50 %;
- reducción supuesta del esfuerzo abordado de 75 %.

El beneficio bruto potencial estimado es cercano a **$12,1 millones CLP anuales**. No es un ahorro demostrado. Debe validarse con un piloto que mida tiempos, reejecuciones, cobertura efectiva y costos reales de error.

## Limitaciones

- Las etiquetas provienen de evidencia de ejecución y no de una evaluación experta independiente.
- La brecha train-test muestra sobreajuste moderado.
- El costo del error utiliza unidades relativas configurables.
- La criticidad de negocio no está disponible en la fuente y no se infiere.
- Los candidatos `upgrade` aún requieren validación mediante una nueva ejecución Gatling.
- La POC no reemplaza la decisión del especialista.

## Estado actual

La POC implementa el pipeline offline completo y deja la validación online en estado `pending_new_execution`. Su aporte demostrado es una recomendación reproducible, explicable y auditable; la mejora operacional y económica debe confirmarse mediante un piloto controlado.

La documentación técnica detallada está disponible en [`app/README.md`](app/README.md).
