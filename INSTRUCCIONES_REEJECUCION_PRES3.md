# Reejecución Pres3 — archivos corregidos

Este paquete contiene únicamente los archivos nuevos o modificados. Extrae el ZIP sobre la raíz de `gatling-ai-performance-copilot` y conserva las rutas incluidas.

## Archivos que se reemplazan

- `app/src/performance_decision_engine/infrastructure/complete_historical_pipeline.py`
- `app/tests/test_complete_historical_pipeline.py`
- `app/scripts/verify_pres3_evidence.py`

## Correcciones incluidas

- Selección del modelo con predicciones OOF de `GroupKFold` sobre entrenamiento.
- Selección del umbral con entrenamiento OOF; el holdout queda solo para evaluación final.
- Comparación pareada Random Forest vs. regresión logística mediante bootstrap por `Build_Id`.
- Recomendaciones de parámetros coherentes con la configuración real:
  - subir `concurrency` o `iterations` aumenta intensidad;
  - bajar `response_time` aumenta exigencia;
  - cada `upgrade` modifica solo un parámetro y exige una nueva ejecución Gatling.
- Conversión de `response_time` a milisegundos para validar la reejecución.
- Costos operativos anuales: USD 100/mes de cloud + USD 10/mes de IA, con tipo presupuestario de 982 CLP/USD.
- Beneficio potencial neto, ROI y payback marcados como proyecciones hasta validación piloto.
- Nuevos artefactos `threshold_oof_analysis.csv` y `paired_model_comparison.csv`.

## Ejecución en PowerShell

Desde la raíz del repositorio:

```powershell
cd .\app
.\.venv\Scripts\activate
pip install -e ".[dev]"
python -m pytest -q
```

Para preservar los resultados anteriores, genera primero una carpeta nueva:

```powershell
pde evaluate-complete `
  --source "..\datasaet\resultadoPruebasGatling.txt" `
  --output-dir "..\Resultados\complete_feedback_corrected"

python .\scripts\verify_pres3_evidence.py `
  --output-dir "..\Resultados\complete_feedback_corrected"
```

Cuando confirmes que la verificación termina con `Pres3 evidence verified`, puedes regenerar la ruta oficial:

```powershell
pde evaluate-complete `
  --source "..\datasaet\resultadoPruebasGatling.txt" `
  --output-dir "..\Resultados\complete_feedback"

python .\scripts\verify_pres3_evidence.py
```

## Resultados esperados con el dataset actual

- Filas utilizables: 6.444.
- Modelo seleccionado: Random Forest.
- F1 `not_applies` en holdout: aproximadamente 0,702.
- Umbral seleccionado solo con entrenamiento OOF: 0,10.
- Distribución holdout: 1.269 `review`, 52 `maintain`, 9 `upgrade`.
- Los 9 `upgrade` proponen un cambio controlado: `concurrency high → very_high`, manteniendo `iterations=high` y `response_time=low`.
- Costo operativo anual estimado: CLP 1.296.240.
- Beneficio potencial neto base: CLP 10.799.760; ROI proyectado 833,2%. Estas dos cifras siguen siendo escenarios y no ahorro demostrado.

## Archivos nuevos generados

La ejecución crea, además de los artefactos anteriores:

- `Resultados/complete_feedback_corrected/threshold_oof_analysis.csv`
- `Resultados/complete_feedback_corrected/paired_model_comparison.csv`

No subas la carpeta `complete_feedback_corrected` como resultado oficial hasta revisarla. Para la entrega final, regenera y verifica `Resultados/complete_feedback`.
