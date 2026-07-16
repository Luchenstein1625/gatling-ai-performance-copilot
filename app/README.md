# Performance Decision Engine

Motor de decisión desacoplado para apoyar el diseño, análisis y recomendación de configuraciones de pruebas de rendimiento.

El caso de estudio inicial utiliza **Gatling**. El dominio permanece independiente de Gatling, YAML, JSON, FastAPI, Typer y mecanismos concretos de persistencia.

---

# Estado actual

**H8 — Machine Learning: ✅ implementación completada**

**Próximo hito: H9 — Explainability**

Quality Gates:

- ✅ Black
- ✅ Ruff
- ✅ MyPy
- ✅ Pytest
- ✅ 61 tests pasando

---

# Arquitectura

```text
app/
├── src/
│   └── performance_decision_engine/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── interfaces/
├── docs/
├── examples/
├── scripts/
├── tests/
└── pyproject.toml
```

La implementación mantiene:

- Clean Architecture;
- Domain Driven Design;
- SOLID;
- tipado estricto;
- inversión de dependencias;
- compatibilidad incremental entre hitos.

---

# Capas

## Domain

Contiene el conocimiento del negocio y los modelos reutilizados por los hitos existentes:

- `Triplet`
- `EndpointConfiguration`
- `PerformanceConfiguration`
- `ExecutionMetrics`
- `NormalizedExecution`
- `Recommendation`
- `Quadrant`
- servicios de dominio

H8 no incorpora dependencias de Machine Learning dentro del dominio.

## Application

Casos de uso implementados:

- `NormalizeExecution`
- `RecommendExecution`
- `GenerateDatasetRow`
- `TrainModel`

La capa de aplicación coordina el flujo y depende de contratos, no de detalles concretos del entrenamiento.

## Infrastructure

Adaptadores implementados:

- YAML Configuration Parser
- Parameter Values Parser
- Gatling Metrics Parser
- Assertions Parser
- JSON Repository
- descubrimiento de ejecuciones históricas
- backend de entrenamiento basado en Decision Tree
- persistencia de artefactos del modelo mediante el backend H8

## Interfaces

- CLI
- REST API

La CLI incorpora los comandos existentes de H1–H8, incluyendo generación de dataset, importación histórica por lotes y entrenamiento.

---

# Requisitos

- Python 3.11+
- pip
- virtualenv

Dependencias de H8 declaradas en `pyproject.toml`:

- `scikit-learn`
- `joblib`

---

# Instalación

Desde la carpeta `app`:

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
pde --version
```

## Quality Gates

```powershell
black --check .
ruff check .
mypy src
pytest
```

Estado confirmado:

```text
61 passed
```

---

# Flujo H1–H8

```text
performance.yaml
        +
parametricConfigurationValues.yaml
        +
global_stats.json
        +
assertions.json (opcional)
        │
        ▼
NormalizeExecution
        │
        ▼
NormalizedExecution
        │
        ├──────────────► RecommendExecution
        │                        │
        │                        ▼
        │                 Recommendation
        │                        │
        └────────────────────────┤
                                 ▼
                       GenerateDatasetRow
                                 │
                                 ▼
                       CSV schema version 1
                                 │
                                 ▼
                  Batch execution discovery/import
                                 │
                                 ▼
                       Dataset validation
                                 │
                                 ▼
                            TrainModel
                                 │
                                 ▼
                 Decision Tree training backend
```

---

# H6 — Decision Matrix

El Recommendation Engine transforma un `NormalizedExecution` en una `Recommendation`.

La decisión determinística continúa siendo el baseline oficial y no es reemplazada por H8.

Reglas existentes:

- solicitudes fallidas → `review`;
- P95 superior al objetivo → `review`;
- assertions fallidas → `review`;
- ejecución sin solicitudes → `review`;
- ejecución sin endpoints habilitados → `review`;
- ejecución satisfactoria → `maintain`.

---

# H7 — Dataset Generation

H7 incorpora `GenerateDatasetRow` y el comando de generación de dataset.

Garantías:

- una ejecución produce una fila;
- `schema_version` identifica el contrato;
- `metrics_scope` conserva el valor `execution`;
- `recommendation_action` utiliza la decisión H6;
- los valores ausentes permanecen ausentes;
- no se inventan criticidad, complejidad ni cuadrantes;
- el encabezado CSV se valida antes de anexar registros.

La importación histórica respeta la siguiente regla:

> Una carpeta con fecha equivale exactamente a una ejecución real.

Los archivos Gatling contenidos dentro de esa carpeta pertenecen a la misma ejecución.

---

# H8 — Machine Learning

H8 implementa el baseline supervisado sobre el dataset H7.

Componentes confirmados:

- `application/use_cases/train_model.py`
- `infrastructure/batch_execution_discovery.py`
- `infrastructure/decision_tree_training_backend.py`
- integración en `interfaces/cli/main.py`
- tests del caso de uso;
- tests del backend;
- tests del descubrimiento histórico;
- validaciones adicionales del Assertions Parser.

## Salvaguardas

Antes de entrenar, H8 valida que:

- el dataset pueda leerse;
- el contrato sea compatible;
- exista información suficiente;
- la variable objetivo contenga al menos dos clases;
- no se publiquen resultados de entrenamiento inexistentes.

H8 no genera datos sintéticos y no oculta limitaciones del dataset.

---

# Estado real del dataset

| Métrica | Valor |
|---|---:|
| Ejecuciones históricas reales | 11 |
| `maintain` | 11 |
| `review` | 0 |

El importador `dataset-batch` funciona correctamente.

El entrenamiento no puede ejecutarse actualmente porque la etiqueta contiene una sola clase. Este resultado es esperado y demuestra que la validación implementada funciona.

Durante los próximos días se incorporarán nuevas ejecuciones reales con errores para obtener ejemplos `review`.

---

# Limitaciones actuales

- Las métricas disponibles tienen alcance de ejecución.
- No existen métricas individuales por endpoint.
- Las recomendaciones H6 son globales para la ejecución.
- El histórico sólo contiene una clase objetivo.
- No existe todavía evidencia válida para reportar métricas de un modelo entrenado.

Estas limitaciones no deben ocultarse ni resolverse mediante datos sintéticos.

---

# Estado del roadmap

| Hito | Estado |
|---|---|
| H1 | ✅ |
| H2 | ✅ |
| H3 | ✅ |
| H4 | ✅ |
| H5 — Normalization | ✅ |
| H6 — Decision Matrix | ✅ |
| H7 — Dataset Generation | ✅ |
| H8 — Machine Learning | ✅ Implementación completada |
| H9 — Explainability | ⏳ Próximo |
| H10 — Integration | ⏳ |

---

# Próximo hito

## H9 — Explainability

H9 debe diseñarse después de revisar por completo la arquitectura y la implementación de H1–H8.

El cierre de H8 no incorpora código, carpetas ni decisiones anticipadas para H9.

---

# Licencia

MIT License.
