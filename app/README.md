# Performance Decision Engine

Motor desacoplado para apoyar decisiones de configuración en pruebas de rendimiento.

El caso de estudio inicial utiliza archivos YAML y resultados Gatling, pero el núcleo del sistema no depende de una herramienta específica. Nuevas fuentes como JMeter, k6 o LoadRunner pueden incorporarse mediante adaptadores sin modificar el dominio.

---

# Arquitectura

```
app/
├── src/performance_decision_engine/
│   ├── domain/
│   │   ├── entities/
│   │   └── services/
│   ├── application/
│   │   ├── ports/
│   │   └── use_cases/
│   ├── infrastructure/
│   │   ├── parsers/
│   │   └── repositories/
│   └── interfaces/
│       ├── cli/
│       └── api/
├── tests/
├── examples/
├── docs/
├── scripts/
└── pyproject.toml
```

---

# Responsabilidades

## domain/

Contiene únicamente el conocimiento del negocio.

Incluye:

- Tripleta
- Configuración de endpoint
- Métricas
- Cuadrantes
- Recomendaciones
- Reglas de dominio

El dominio no conoce:

- YAML
- JSON
- Gatling
- FastAPI
- Typer
- Persistencia

---

## application/

Contiene los casos de uso.

Actualmente implementa:

- NormalizeExecution
- Quadrant Resolution

Los siguientes casos de uso serán incorporados durante los próximos hitos:

- Recommendation Engine
- Explainability
- Learning Pipeline

---

## infrastructure/

Implementa adaptadores hacia herramientas externas.

Actualmente incluye:

- Parser de performance.yaml
- Parser de parametricConfigurationValues.yaml
- Parser de global_stats.json
- Parser de assertions.json
- Repositorio JSON

---

## interfaces/

Expone la funcionalidad del sistema mediante:

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

# Verificación

```powershell
pde doctor
```

```powershell
pde --version
```

```powershell
pytest
```

---

# Estado actual

Actualmente el proyecto implementa completamente:

- Arquitectura limpia
- CLI
- API REST
- Parser YAML
- Parser de parámetros
- Parser de métricas Gatling
- Parser de assertions
- Resolución de cuadrantes
- Normalización de configuraciones
- Normalización de métricas
- Persistencia JSON
- Modelo `NormalizedExecution`
- Validaciones automáticas
- Warnings
- Pruebas unitarias

---

# Calidad

El proyecto pasa satisfactoriamente:

- ✅ Black
- ✅ Ruff
- ✅ MyPy
- ✅ Pytest

45 pruebas automatizadas aprobadas.

---

# Ejecución

Para validar el entorno:

```powershell
pde doctor
```

Para obtener la versión:

```powershell
pde --version
```

Para ejecutar las pruebas:

```powershell
pytest
```

---

# Normalización

El principal caso de uso implementado durante el Hito 5 corresponde a la normalización de una ejecución completa de pruebas de rendimiento.

El proceso combina la configuración de la prueba con los resultados generados por Gatling para producir un modelo único de dominio denominado `NormalizedExecution`.

---

## Ejecutar normalización

```powershell
pde normalize `
    --performance examples/input/performance.yaml `
    --parameters examples/input/parametricConfigurationValues.yaml `
    --results examples/input/global_stats.json `
    --output examples/output/execution_summary.json
```

Si existen assertions:

```powershell
pde normalize `
    --performance examples/input/performance.yaml `
    --parameters examples/input/parametricConfigurationValues.yaml `
    --results examples/input/global_stats.json `
    --assertions examples/input/assertions.json `
    --output examples/output/execution_summary.json
```

---

## Salida

El proceso genera un archivo JSON con la representación normalizada de la ejecución.

La salida contiene:

- Configuración resuelta
- Endpoints
- Tripletas
- Métricas globales
- Percentiles
- TPS
- Error Rate
- Assertions
- Warnings

---

# Resolver cuadrante

Ejemplo:

```powershell
pde quadrant `
    --criticality high `
    --complexity medium
```

Resultado esperado:

```
Quadrant: 6
```

---

# API REST

Levantar la API:

```powershell
uvicorn performance_decision_engine.interfaces.api.main:app --reload
```

Endpoints disponibles:

```
GET /health

GET /version

GET /quadrants/{criticality}/{complexity}
```

Durante H6 se incorporarán nuevos endpoints para recomendaciones inteligentes.

---

# Flujo funcional

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
Recommendation Engine (H6)
```

---

# Estado del proyecto

## Implementado

- Arquitectura limpia
- CLI
- API REST
- YAML Parser
- Parameter Resolver
- Gatling Metrics Parser
- Assertions Parser
- Normalization Engine
- JSON Repository
- Quadrant Resolution
- Unit Testing

---

## En desarrollo

- Recommendation Engine
- Explainability
- Machine Learning
- Recommendation Repository
- Recommendation API

---

# Calidad

El proyecto mantiene como requisito obligatorio que todos los cambios aprueben:

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

**45 pruebas aprobadas.**

---

# Roadmap

| Hito | Estado |
|------|--------|
| H1 | ✅ |
| H2 | ✅ |
| H3 | ✅ |
| H4 | ✅ |
| H5 | ✅ |
| H6 | ⏳ |
| H7 | ⏳ |
| H8 | ⏳ |

---

# Próximo hito

## H6 – Recommendation Engine

El siguiente objetivo consiste en utilizar el modelo `NormalizedExecution` para generar recomendaciones automáticas sobre la configuración óptima de pruebas de rendimiento.

El motor incorporará:

- reglas de negocio;
- recomendaciones baseline;
- persistencia;
- explicaciones;
- integración con la API REST.

---

# Licencia

MIT License.