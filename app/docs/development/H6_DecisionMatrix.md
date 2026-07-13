# H6 – Recommendation Engine

## Introducción

El Recommendation Engine constituye el sexto hito del proyecto **Gatling AI Performance Copilot**.

Su objetivo consiste en generar una recomendación automática a partir de una ejecución completamente normalizada de pruebas de rendimiento.

La implementación corresponde al primer motor de decisión del sistema y establece la base para la incorporación futura de:

- Explainability
- Machine Learning
- Aprendizaje supervisado
- Modelos predictivos
- Recomendaciones inteligentes

---

# Objetivos

El H6 busca:

- consumir únicamente un `NormalizedExecution`;
- desacoplar completamente el dominio de Gatling;
- generar recomendaciones determinísticas;
- reutilizar el conocimiento experto existente;
- producir evidencia estructurada;
- preparar el dominio para IA.

---

# Arquitectura

La recomendación se genera utilizando el siguiente flujo:

```
performance.yaml
        +
parametricConfigurationValues.yaml
        +
global_stats.json
        +
assertions.json (opcional)
        │
        ▼
Infrastructure Parsers
        │
        ▼
NormalizeExecution
        │
        ▼
NormalizedExecution
        │
        ▼
RecommendExecution
        │
        ▼
Recommendation
```

La entrada del Recommendation Engine es exclusivamente el modelo de dominio `NormalizedExecution`.

No existe dependencia directa con:

- YAML
- JSON
- Gatling
- FastAPI
- Typer
- Persistencia

---

# Recommendation Engine

El Recommendation Engine implementa un conjunto inicial de reglas baseline.

Estas reglas representan conocimiento experto previamente utilizado durante el proceso manual de análisis.

El motor no realiza aprendizaje.

Todas las decisiones son completamente determinísticas.

---

# Reglas implementadas

## Error Rate

Cuando la ejecución presenta solicitudes fallidas:

```
error_rate > 0
```

↓

```
review
```

---

## Tiempo de respuesta

Cuando:

```
P95 > Response Time configurado
```

↓

```
review
```

---

## Assertions

Cuando existen assertions y alguna falla:

```
failed assertions
```

↓

```
review
```

---

## Ejecución vacía

Cuando:

```
total_requests == 0
```

↓

```
review
```

---

## Endpoints

Cuando no existen endpoints habilitados:

```
enabled_endpoints == 0
```

↓

```
review
```

---

## Caso satisfactorio

Cuando todas las validaciones anteriores son correctas:

```
maintain
```

---

# Recommendation

La salida del motor corresponde a la entidad de dominio:

```
Recommendation
```

Compuesta por:

```
Recommendation

├── action

├── explanation

└── evidence
```

---

# Recommendation JSON

Ejemplo:

```json
{
  "action": "maintain",
  "explanation": "Las reglas básicas evaluadas no detectaron incumplimientos.",
  "evidence": {
    "error_rate_percent": 0,
    "p95_response_time_ms": 1465,
    "expected_response_time_ms": 15000,
    "total_requests": 2801,
    "successful_requests": 2801,
    "failed_requests": 0,
    "enabled_endpoints": [
      "buscar consentimiento"
    ],
    "endpoint_response_time_targets_ms": {
      "buscar consentimiento": 15000
    },
    "metrics_scope": "execution",
    "warnings": []
  }
}
```

---

# Caso de uso

El Recommendation Engine incorpora el caso de uso:

```
RecommendExecution
```

Entrada:

```
NormalizedExecution
```

Salida:

```
Recommendation
```

---

# CLI

El Recommendation Engine puede ejecutarse desde la línea de comandos.

```
pde recommend `
    --performance examples/input/performance.yaml `
    --parameters examples/input/parametricConfigurationValues.yaml `
    --results examples/input/global_stats.json `
    --output examples/output/recommendation.json
```

Resultado:

```
Recommendation: maintain

Las reglas básicas evaluadas no detectaron incumplimientos.

Created:

examples/output/recommendation.json
```

---

# REST API

La API incorpora el endpoint:

```
POST /recommendations
```

Entrada:

```
NormalizedExecution
```

Salida:

```
Recommendation
```

---

# Limitaciones actuales

La implementación H6 utiliza únicamente la información disponible dentro de `NormalizedExecution`.

Actualmente:

- las métricas corresponden a la ejecución completa;
- no existen métricas individuales por endpoint;
- las recomendaciones son globales.

No se realizan inferencias por endpoint.

---

# Decisiones de diseño

Durante H6 se decidió:

- mantener compatibilidad con los hitos anteriores;
- reutilizar la entidad `Recommendation`;
- reutilizar el servicio baseline existente;
- evitar nuevas capas innecesarias;
- mantener un dominio independiente de frameworks.

Estas decisiones permiten incorporar Machine Learning sin modificar la arquitectura actual.

---

# Calidad

El H6 mantiene todos los estándares definidos para el proyecto.

Se validó exitosamente mediante:

```
black --check .

ruff check .

mypy src

pytest
```

Resultado:

- ✅ Black
- ✅ Ruff
- ✅ MyPy
- ✅ Pytest

---

# Cobertura

Estado actual:

```
50 pruebas automatizadas aprobadas
```

Incluyendo:

- YAML Parser
- Parameter Resolver
- Gatling Parser
- Assertions Parser
- NormalizeExecution
- Recommendation Engine
- Quadrant Resolution

---

# Evolución futura

## H7

El siguiente hito incorporará Explainability.

Se espera implementar:

- explicación detallada de recomendaciones;
- trazabilidad de reglas;
- evidencia enriquecida;
- auditoría de decisiones.

---

## H8

Posteriormente el Recommendation Engine evolucionará incorporando:

- Machine Learning;
- entrenamiento supervisado;
- modelos predictivos;
- aprendizaje con ejecuciones históricas;
- recomendación inteligente;
- Dashboard de apoyo para especialistas.

---

# Resultado del H6

Al finalizar este hito el proyecto incorpora exitosamente:

- Recommendation Engine
- RecommendExecution
- Recommendation JSON
- Recommendation CLI
- Recommendation API
- Reglas baseline
- Integración con `NormalizedExecution`

manteniendo:

- compatibilidad con H1–H5;
- Clean Architecture;
- Domain Driven Design;
- SOLID;
- tipado estático;
- calidad mediante Black, Ruff, MyPy y Pytest.

El Recommendation Engine constituye la base sobre la cual evolucionarán los hitos H7 (Explainability) y H8 (Machine Learning).