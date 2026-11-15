# A5 · Mapa de información y decisiones

| Decisión | Información disponible | Uso del test v3 | Clasificación |
|---|---|---|---|
| Familia de modelos | Exploraciones v2 y estabilidad sobre el universo histórico | Algunos builds pudieron aparecer en holdouts previos | Exploratoria previa |
| Variables: Concurrency, Iterations, ResponseTime | Definidas antes del protocolo v3, apoyadas por análisis histórico | No se cambiaron después de abrir el test | Congelada con exposición histórica |
| Hiperparámetros | Train v3 | Ninguno | Selección interna válida |
| Calibración y threshold | OOF train + dev v3 | Ninguno | Selección interna válida |
| Política operacional | Train/dev y guardrails preinscritos | Test solo evaluación | Congelada |
| Métricas finales | Test v3 abierto una vez | Evaluación descriptiva | Oficial v3 |
| Sensibilidad sin builds del holdout fijo v2 | Subconjunto preinscrito del test | Diagnóstico post-hoc | No cambia selección |

## Frase de limitación

De los 104 builds del test v3, 25 (24.0%) habían aparecido en el holdout exploratorio v2; 79 no habían aparecido allí. Además, los 20 splits exploratorios de estabilidad reutilizaron builds del universo histórico. El test v3 no se usó para ajustar hiperparámetros, calibración ni umbral, pero la familia de modelos y las variables se definieron tras exploraciones históricas; por ello, la evaluación se interpreta como confirmación interna y requiere validación prospectiva externa.

## Regla

El análisis A5 no autoriza reentrenar, cambiar variables, reemplazar el modelo ni seleccionar un resultado usando el test.
