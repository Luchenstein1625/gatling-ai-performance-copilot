# H6 – Recommendation Engine

## Objetivo

Implementar un motor de recomendación desacoplado de los parsers y de Gatling. El motor recibe un
`NormalizedExecution` y produce una recomendación determinística, tipada y explicable mediante
reglas de dominio.

## Decisiones

- La entrada canónica es `NormalizedExecution`.
- Las métricas actuales son globales para la ejecución.
- El motor no inventa valores numéricos que no estén presentes en la entrada.
- Una ejecución saludable conserva su configuración (`KEEP`).
- Errores, assertions fallidas o tiempos sobre objetivo requieren revisión (`REVIEW`).
- Datos incompletos producen `INSUFFICIENT_DATA`.
- La evidencia se representa de forma estructurada para preparar Explainability y Machine Learning.

## Componentes

- `Recommendation` y `EndpointRecommendation`.
- Value Objects de decisión, alcance, tripleta recomendada y evidencia.
- Reglas de datos, assertions, errores, tiempos de respuesta y estabilidad.
- `RecommendationService`.
- Puerto `RecommendationEngine`.
- Caso de uso `GenerateRecommendation`.
- Adaptador `RuleBasedRecommendationEngine`.
- Repositorio `JsonRecommendationRepository`.
- Comando CLI `pde recommend`.
- Endpoint `POST /recommendations`.

## CLI

```powershell
pde recommend `
    --performance examples/input/performance.yaml `
    --parameters examples/input/parametricConfigurationValues.yaml `
    --results examples/input/global_stats.json `
    --assertions examples/input/assertions.json `
    --output examples/output/recommendation.json
```

`--assertions` es opcional.

## API

```text
POST /recommendations
```

El cuerpo corresponde a un `NormalizedExecution` y la respuesta a un `Recommendation`.

## Definition of Done

- El motor consume `NormalizedExecution` sin conocer Gatling ni YAML.
- Las reglas son puras, determinísticas y testeables.
- La recomendación incluye evidencia y reglas evaluadas.
- CLI y API utilizan el mismo caso de uso.
- La persistencia JSON es intercambiable mediante un puerto.
- Las pruebas existentes continúan aprobando.
- Black, Ruff, MyPy y Pytest finalizan sin errores.
