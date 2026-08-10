# Estado de mejoras Pres3 — versión 1.6.0

## Completado con evidencia disponible

| Mejora | Evidencia |
|---|---|
| EDA relacional | p95, RPS, errores y valores faltantes por clase |
| Comparación de modelos | Árbol, regresión logística, Random Forest y baseline |
| Holdout sin fuga | Partición agrupada por `Build_Id`, solapamiento 0 |
| Validación cruzada | 5-fold `GroupKFold`; F1 medio 0,8049 |
| Sensibilidad | 17 cut-offs entre 0,10 y 0,90 |
| Función de costo | Costos relativos configurables y auditables |
| Umbral seleccionado | 0,35; recall 0,8808; F1 0,8061 |
| Análisis segmentado | Métricas por pilar y componente con soporte >= 20 |
| Seguridad operacional | `review` no modifica configuración; `downgrade` es humano |
| Recomendación por capas | Aplicabilidad, decisión, optimización y contrato de validación |

## Pendiente porque requiere nueva evidencia

| Pendiente | Evidencia necesaria |
|---|---|
| Validación experimental de `upgrade` | Ejecutar en Gatling una muestra aprobada |
| Aprobación del nuevo cuadrante | Resultado exitoso, 0 errores y sin regresión |
| Costos monetarios definitivos | Tiempos y costos observados durante el piloto |
| Etiquetas independientes | Revisión de especialistas sin usar la regla derivada |
| Beneficio económico demostrado | Comparación real antes/después del piloto |

Una recomendación `upgrade` mantiene el estado `pending_new_execution` hasta que exista
una nueva ejecución Gatling. Si falla o queda incompleta, retorna a `review` y no provoca
un `downgrade` automático.
