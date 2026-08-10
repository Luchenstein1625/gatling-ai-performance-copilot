# Defensa: Afirmacion, Evidencia y Limite

## Base utilizada (corrida vigente)
- app/examples/output/run_20260803_185120/auto_evaluation_summary.json
- app/examples/output/run_20260803_185120/historical_model_report.json
- app/examples/output/run_20260803_185120/multiseed_evaluation.json
- app/examples/output/run_20260803_185120/multiseed_evaluation_splits.csv
- app/examples/output/run_20260803_185120/statistical_validity_report.json
- app/examples/output/runs_comparison_latest.json

## Tabla de defensa

| Afirmacion en presentacion | Evidencia cuantitativa disponible | Limite que debes declarar |
|---|---|---|
| La evaluacion se hizo sobre una muestra historica acotada | 28 filas, split 21 train / 7 test | Es evidencia sobre esta muestra, no garantia universal |
| Se aplico evaluacion repetida con multiples semillas | repeated_stratified_holdout, 30 seeds, test_size 0.25, detalle por split y_true/y_pred | Las particiones provienen de la misma muestra de 28 casos |
| El modelo operacional supera baseline pero no llega a fidelidad perfecta | Macro-F1 operational_core mean = 0.5987, baseline macro-F1 = 0.4167, mejora = 0.1820 | Mejora moderada dentro de muestra pequena |
| Las variantes con proxies muestran brecha respecto a operational_core | all_features mean = 1.0000 vs operational_core mean = 0.5987, gap = 0.4013 | Indicio de dependencia de proxies o leakage |
| La brecha de sobreajuste es estadisticamente direccional | Delta pareado mean = 0.4013, IC95 [0.3391 ; 0.4635], includes_zero = false, evidence = strong | No implica causalidad fuera de esta muestra |
| El pipeline de datos tiene alta cobertura para esta corrida | discovered = 29, imported_this_run = 28, skipped = 1, failed = 0 | Repetir control de calidad en nuevas cargas |
| La calidad de datos es consistente para variables usadas | duplicate_rows = 0; p90_response_time_ms vacia (28/28), resto usado con 0 nulos | p90 no aporta y debe mantenerse excluida o reconstruida |
| El enfoque es apoyo y no reemplazo experto | salida maintain/review/evolve + validacion humana obligatoria | Falta validacion con etiquetas expertas independientes |

## Evidencia inferencial minima con datos vigentes
- operational_core Macro-F1 mean = 0.5987; std = 0.1738; IC95 [0.5365 ; 0.6609].
- all_features Macro-F1 mean = 1.0000; without_assertions Macro-F1 mean = 1.0000.
- Delta pareado (all_features - operational_core) = 0.4013; IC95 [0.3391 ; 0.4635].
- Clasificacion automatica del reporte: evidence = strong; overfit risk en comparador = high.
- Lectura para defensa: hay evidencia direccional de brecha entre variantes proxy-rich y operational_core; por tanto, el modelo actual se reporta como POC explicable con control de sobreajuste, no como solucion generalizable cerrada.

## Umbrales iniciales vigentes (alineados a 30 semillas)
- Completitud por variable critica >= 95%
- Cobertura importacion (importadas/detectadas) >= 95%
- Macro-F1 operational_core >= 0.55
- Balanced accuracy operational_core >= 0.55
- Desviacion estandar de Macro-F1 operational_core <= 0.20
- Mejora de Macro-F1 operational_core frente a baseline >= 0.15
- Monitoreo de brecha de sobreajuste: all_features - operational_core (reportada con IC95)

## Respuesta corta sugerida ante preguntas dificiles
- "No presentamos 1.0 como desempeno final del sistema; la metrica clave para decision hoy es operational_core (Macro-F1 0.5987 con IC95), mientras que 1.0 en variantes con proxies se reporta como riesgo de sobreajuste."
- "La diferencia entre variantes es estadisticamente direccional en esta muestra (delta 0.4013, IC95 sin 0), por eso mantenemos validacion humana obligatoria."
- "La siguiente validacion obligatoria es por microservicio y con etiquetas expertas independientes para probar generalizacion real."
