# Aplicación del feedback del profesor evaluador 02

## Reformulación del proyecto completo

**Objetivo general:** desarrollar y evaluar un copiloto explicable que determine si la
configuración y el cuadrante actual deben **mantenerse**, evaluarse en un cuadrante más
exigente o pasar a **revisión humana**, usando las características y los resultados
históricos de las pruebas Gatling.

## Objetivos específicos

1. Integrar y depurar configuración, métricas e historial de pruebas Gatling en un dataset
   reproducible, con controles de calidad y prevención de fuga de información.
2. Entrenar y comparar tres algoritmos para recomendar `review`, `maintain` o `upgrade`,
   priorizando la detección de ejecuciones que requieren revisión.
3. Evaluar la generalización con un conjunto de prueba independiente por `Build_Id`, usando
   matriz de confusión, precision, recall y F1 para entrenamiento y prueba.
4. Explicar la decisión mediante el árbol, reglas y variables relevantes, conservando la
   aprobación humana antes de modificar o ejecutar pruebas.
5. Optimizar los parámetros operacionales mediante perfiles robustos de ejecuciones exitosas
   comparables, limitando cada propuesta a un solo nivel y exigiendo aprobación humana.
6. Evaluar offline la generalización y validar posteriormente cada propuesta aprobada con el
   resultado real de una nueva ejecución Gatling.

## Trazabilidad feedback → implementación

| Indicación | Aplicación |
|---|---|
| Dataset anterior demasiado pequeño | Importador para el nuevo histórico de más de 6.000 filas. |
| Prueba correcta, irregular o exacta | Salida `upgrade`, `review` o `maintain`. |
| Probar tres modelos | Árbol, regresión logística y random forest. |
| Simplificar evaluación | Matriz de confusión, precision, recall y F1 en train/test. |
| Las fallas deben revisarse | Toda falla, omisión, irregularidad o dato incompleto produce `review`. |
| No bajar automáticamente | `downgrade` queda reservado a una decisión humana posterior. |
| Mostrar el árbol | Exportación DOT y reglas de texto. |
| Corregir la validación | Holdout agrupado por `Build_Id`, sin solapamiento entre conjuntos. |
| Objetivos del proyecto completo | Objetivos reformulados desde clasificación hasta recomendación futura. |
| Primera capa binaria | `applies/not_applies`, comparada con árbol, regresión logística, random forest y baseline mayoritario. |
| Optimización de parámetros | Perfiles de pares exitosos para `Concurrency`, `Iterations` y `ResponseTime`; máximo un nivel por propuesta. |
| Evaluar recomendación | Holdout independiente y contrato implementado para validar una reejecución Gatling real. |

## Criterio metodológico

El archivo real `datasaet/resultadoPruebasGatling.txt` es la entrada del proceso. Sus
métricas posteriores construyen una etiqueta auditable, pero se excluyen de los predictores
para evitar fuga de información. `apdex` no se usa porque el export contiene una referencia
Java y `rating` está vacío. `review` se asigna ante `Performance=0`, estado distinto de
`Success`, errores o métricas esenciales incompletas; `upgrade` exige éxito, cero errores y
`p95 <= 1500 ms`; los demás casos exitosos quedan en `maintain`. Un `upgrade` solo propone
evaluar el cuadrante siguiente y siempre requiere aprobación humana.

## Arquitectura completa implementada

1. **Aplicabilidad:** estima `applies` o `not_applies` sin variables posteriores que revelen
   el resultado.
2. **Decisión:** convierte la evidencia en `review`, `maintain` o `upgrade`. Las fallas nunca
   bajan automáticamente.
3. **Optimización:** aprende configuraciones de pares exitosos usando solo entrenamiento,
   propone como máximo un nivel de cambio y calcula un cuadrante operacional 1–9.
4. **Evaluación:** informa métricas train/test, preserva grupos por `Build_Id` y deja cada
   propuesta `upgrade` como `pending_new_execution` hasta recibir el nuevo resultado real.

El cuadrante calculado en la capa 3 representa **intensidad operacional de la configuración**.
No se presenta como criticidad de negocio, porque esa variable no existe en el archivo fuente.

Ejecución integral:

```powershell
pde evaluate-complete `
  --source ".\datasaet\resultadoPruebasGatling.txt" `
  --output-dir ".\Resultados\complete_feedback"
```
