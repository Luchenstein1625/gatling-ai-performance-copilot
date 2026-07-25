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

## Alcance actual

La regla y su traducción a una acción humana están implementadas y probadas. La
integración con el pipeline requiere que el dataset incorpore un identificador
estable del componente. Los 28 registros actuales no contienen ese campo, por lo
que no deben reetiquetarse artificialmente como `evolve`.
