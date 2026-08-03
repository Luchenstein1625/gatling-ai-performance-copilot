# POC - Recomendación de evolución de carga

## Objetivo

Complementar las recomendaciones `maintain` y `review` con `evolve`, sin aumentar
automáticamente la carga ni cambiar el cuadrante.

## Regla inicial

Una recomendación `review` nunca puede ser reemplazada por `evolve`.

Un componente es candidato a `evolve` solamente cuando sus tres ejecuciones
comparables más recientes cumplen simultáneamente:

- recomendación `maintain`;
- cero por ciento de errores;
- todas las assertions aprobadas;
- p95 menor o igual al 70 % del objetivo de tiempo de respuesta.

La salida propone evaluar un aumento controlado de carga del 10 %. La aprobación
del especialista continúa siendo obligatoria.

## Entradas requeridas

Cada observación histórica debe incluir:

- `component_id`;
- `recommendation_action`;
- `p95_response_time_ms`;
- `response_time_target_ms`;
- `error_rate_percent`;
- `assertions_all_passed`.

Las observaciones se entregan ordenadas desde la más antigua hasta la más reciente.
Solo se comparan registros con el mismo `component_id`.

## Salidas

| Recomendación | Significado |
|---|---|
| `review` | Existe un incumplimiento y debe revisarse la configuración. |
| `maintain` | La ejecución cumple, pero no existe evidencia suficiente para exigir más carga. |
| `evolve` | Existe estabilidad histórica para evaluar un incremento controlado de carga. |

Para `evolve`, `PlanQuadrantAction` genera:

```json
{
  "action": "evaluate_load_increase",
  "proposed_load_increase_percent": 10,
  "human_validation_required": true
}
```

## Ejecución integrada

La evaluación histórica está conectada de forma opcional a
`scripts/run_august_poc.ps1`. Se debe agregar:

```powershell
-ComponentId "ms-loyalty-ofertas" `
-EvolutionHistory ".\examples\input\evolution_history.csv"
```

Si ambos parámetros se omiten, el pipeline conserva exactamente el comportamiento
anterior. Si se informa solo uno, la ejecución se detiene para evitar una evaluación
sin identidad o sin historial.

Con historial, se genera un noveno artefacto:

```text
evolution_recommendation.json
```

`quadrant_action.json` se construye a partir de esa recomendación evaluada.

## Formato del historial

```csv
component_id,recommendation_action,p95_response_time_ms,response_time_target_ms,error_rate_percent,assertions_all_passed
ms-loyalty-ofertas,maintain,900,2000,0,True
ms-loyalty-ofertas,maintain,980,2000,0,True
ms-loyalty-ofertas,maintain,1050,2000,0,True
```

Las filas deben ir de la más antigua a la más reciente. El identificador debe ser
estable y definido por el equipo; no se infiere desde rutas o nombres de archivos.

## Alcance del modelo

`evolve` es una recomendación determinística posterior a H6 y H8. El árbol H8
continúa entrenado con `maintain` y `review`, porque los 28 registros disponibles no
incluyen identidad histórica ni ejemplos validados de `evolve`. La nueva capacidad
es operativa dentro del pipeline, pero no debe presentarse como una tercera clase
aprendida por Machine Learning hasta disponer de datos etiquetados suficientes.
