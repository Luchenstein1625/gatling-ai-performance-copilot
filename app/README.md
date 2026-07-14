# Performance Decision Engine

Motor de decisión desacoplado para apoyar el diseño, análisis y recomendación de configuraciones de pruebas de rendimiento.

El caso de estudio inicial utiliza **Gatling**, sin embargo el núcleo del sistema fue diseñado para ser completamente independiente de cualquier herramienta específica.

La arquitectura permite incorporar futuras fuentes de información como:

- JMeter
- k6
- LoadRunner
- NeoLoad
- Herramientas propietarias

mediante adaptadores de infraestructura sin modificar el dominio.

---

# Objetivos

El Performance Decision Engine tiene como propósito:

- interpretar configuraciones de pruebas;
- resolver parámetros corporativos;
- normalizar configuraciones y resultados;
- construir un modelo único de dominio;
- generar recomendaciones automáticas;
- preparar la incorporación de Explainable AI y Machine Learning.

---

# Arquitectura

El proyecto implementa una arquitectura basada en **Clean Architecture** y **Domain Driven Design**.

```
app/

├── src/
│
├── performance_decision_engine/
│
│   ├── domain/
│   │
│   ├── application/
│   │
│   ├── infrastructure/
│   │
│   └── interfaces/
│
├── docs/
│
├── examples/
│
├── scripts/
│
├── tests/
│
└── pyproject.toml
```

---

# Capas

## Domain

Contiene únicamente el conocimiento del negocio.

Implementa:

- Triplet
- EndpointConfiguration
- PerformanceConfiguration
- ExecutionMetrics
- NormalizedExecution
- Recommendation
- Quadrant
- Servicios de dominio

El dominio no depende de:

- YAML
- JSON
- Gatling
- FastAPI
- Typer
- Persistencia

---

## Application

Implementa los casos de uso.

Actualmente:

- NormalizeExecution
- RecommendExecution

Los casos de uso reciben entidades de dominio y delegan las decisiones a los servicios correspondientes.

---

## Infrastructure

Contiene los adaptadores externos.

Actualmente implementa:

- YAML Configuration Parser
- Parameter Values Parser
- Gatling Metrics Parser
- Assertions Parser
- JSON Repository

Esta capa es responsable únicamente de traducir datos externos al modelo interno.

---

## Interfaces

Expone el sistema mediante:

- CLI
- REST API

---

# Requisitos

- Python 3.11+
- pip
- virtualenv

---

# Instalación

Desde la carpeta **app**:

```powershell
python -m venv .venv

.\.venv\Scripts\activate

python -m pip install --upgrade pip

pip install -e ".[dev]"
```

---

# Verificación del entorno

```powershell
pde doctor
```

---

## Versión

```powershell
pde --version
```

---

## Ejecutar pruebas

```powershell
pytest
```

---

# Componentes implementados

## Configuración

- YAML Configuration Parser
- Parameter Resolver
- Triplet Resolution
- Endpoint Configuration

---

## Métricas

- Gatling Metrics Parser
- Assertions Parser
- Percentiles
- Error Rate
- TPS
- Response Times

---

## Dominio

- Quadrant Resolution
- NormalizeExecution
- NormalizedExecution
- Recommendation Engine

---

## Persistencia

- JSON Repository

---

## Interfaces

- CLI
- REST API

---

# Decision Matrix (H6)

El Hito 6 incorpora el primer motor de recomendación del proyecto.

Su objetivo consiste en transformar una ejecución normalizada en una recomendación reutilizable por cualquier consumidor del dominio.

## Entrada

El Recommendation Engine recibe únicamente:

```text
NormalizedExecution
```

No conoce:

- Gatling
- YAML
- JSON
- CLI
- REST API

---

## Flujo

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

---

## Recommendation

La salida corresponde a la entidad:

```text
Recommendation
```

Compuesta por:

- action
- explanation
- evidence

---

## Reglas implementadas

### Error Rate

```
error_rate > 0

↓

review
```

---

### Tiempo de respuesta

```
P95 > objetivo

↓

review
```

---

### Assertions

```
assertions failed

↓

review
```

---

### Sin requests

```
requests == 0

↓

review
```

---

### Sin endpoints

```
no enabled endpoints

↓

review
```

---

### Ejecución correcta

```
↓

maintain
```

---

# Normalización

El principal caso de uso desarrollado durante H5 corresponde a la normalización de una ejecución.

El proceso produce un objeto único denominado:

```text
NormalizedExecution
```

que contiene:

- configuración
- endpoints
- tripletas
- métricas
- warnings

Este objeto constituye la representación oficial de una ejecución dentro del dominio.

---

# Ejecutar normalización

```powershell
pde normalize `
    --performance examples/input/performance.yaml `
    --parameters examples/input/parametricConfigurationValues.yaml `
    --results examples/input/global_stats.json `
    --output examples/output/execution_summary.json
```

Con assertions:

```powershell
pde normalize `
    --performance examples/input/performance.yaml `
    --parameters examples/input/parametricConfigurationValues.yaml `
    --results examples/input/global_stats.json `
    --assertions examples/input/assertions.json `
    --output examples/output/execution_summary.json
```

---

# Recommendation CLI

El H6 incorpora un nuevo comando.

```powershell
pde recommend `
    --performance examples/input/performance.yaml `
    --parameters examples/input/parametricConfigurationValues.yaml `
    --results examples/input/global_stats.json `
    --output examples/output/recommendation.json
```

Ejemplo de salida:

```
Recommendation: maintain

Las reglas básicas evaluadas no detectaron incumplimientos.

Created:
examples/output/recommendation.json
```

---

# API REST

Ejecutar:

```powershell
uvicorn performance_decision_engine.interfaces.api.main:app --reload
```

Endpoints:

```
GET /health

GET /version

GET /quadrants/{criticality}/{complexity}

POST /recommendations
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
    "metrics_scope": "execution"
  }
}
```

---

# Limitaciones actuales

Actualmente las métricas corresponden a la ejecución completa.

No existen métricas individuales por endpoint.

Las recomendaciones son globales para toda la ejecución.

---

# Calidad

Todos los cambios deben aprobar:

```powershell
black --check .

ruff check .

mypy src

pytest
```

Estado actual:

- ✅ Black
- ✅ Ruff
- ✅ MyPy
- ✅ Pytest

**50 pruebas automatizadas aprobadas.**

---

# Estado del proyecto

| Hito | Estado |
|------|--------|
| H1 | ✅ |
| H2 | ✅ |
| H3 | ✅ |
| H4 | ✅ |
| H5 – Normalization | ✅ |
| H6 – Decision Matrix | ✅ |
| H7 – Dataset Generation | ⏳ |
| H8 – Machine Learning | ⏳ |
| H9 – Explainability | ⏳ |
| H10 – Integration | ⏳ |
 ✅ |
| H7 | ⏳ |
| H8 | ⏳ |

---

# Próximo Hito

## H7 – Dataset Generation

Se incorporará:

- generación de registros desde `NormalizedExecution`;
- incorporación de la decisión determinística de H6;
- esquema estable y reproducible;
- validaciones de calidad del dataset;
- preparación para entrenamiento supervisado.

---

# H8

Posteriormente el proyecto evolucionará incorporando:

- Machine Learning
- entrenamiento supervisado
- modelos predictivos
- Dashboard
- Explainable AI

---

# Licencia

MIT License.