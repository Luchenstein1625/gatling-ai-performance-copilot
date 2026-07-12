# Performance Decision Engine

Motor desacoplado para apoyar decisiones de configuración en pruebas de rendimiento.

El proyecto implementa una arquitectura limpia (*Clean Architecture*) para separar completamente la lógica de negocio de las herramientas utilizadas para ejecutar las pruebas.

Actualmente el caso de estudio utiliza archivos **YAML** y resultados de **Gatling**, pero el núcleo del sistema no depende de una herramienta específica. Nuevas fuentes como **JMeter**, **k6** o **LoadRunner** pueden incorporarse mediante adaptadores sin modificar el dominio.

---

# Objetivo

El objetivo del proyecto es construir un motor capaz de:

* Interpretar configuraciones de pruebas de rendimiento.
* Normalizar resultados provenientes de distintas herramientas.
* Generar una representación común de las ejecuciones.
* Servir como base para un futuro motor de recomendaciones basado en Machine Learning.

---

# Arquitectura

El proyecto sigue una arquitectura desacoplada basada en **Clean Architecture**.

```text
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

# Componentes

## Domain

Contiene el conocimiento del negocio.

Incluye:

* Tripleta
* Cuadrantes
* Configuración de endpoints
* Métricas de ejecución
* Recomendaciones
* Reglas puras

El dominio no depende de:

* FastAPI
* Typer
* YAML
* Gatling
* Persistencia
* Frameworks externos

---

## Application

Implementa los casos de uso del sistema.

Actualmente incluye:

* Normalización de una ejecución
* Resolución de cuadrantes
* Recomendación Baseline

También define los puertos utilizados para desacoplar el dominio de la infraestructura.

---

## Infrastructure

Implementa los detalles técnicos externos.

Actualmente incorpora:

* Parser de `performance.yaml`
* Parser de `parametricConfigurationValues.yaml`
* Parser de resultados Gatling
* Repositorio JSON

---

## Interfaces

Expone la funcionalidad mediante:

* CLI
* API REST

---

# Requisitos

* Python 3.11 o superior
* Windows, Linux o macOS

---

# Instalación

Desde la carpeta `app`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e ".[dev]"
```

---

# Uso

## Verificar instalación

```powershell
pde doctor
```

---

## Ver versión

```powershell
pde --version
```

---

## Resolver un cuadrante

```powershell
pde quadrant --criticality high --complexity medium
```

Resultado esperado:

```text
Quadrant: 6
```

---

## Normalizar una ejecución

```powershell
pde normalize `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output examples/output/execution_summary.json
```

---

# API REST

Ejecutar:

```powershell
uvicorn performance_decision_engine.interfaces.api.main:app --reload
```

Endpoints disponibles:

* `GET /health`
* `GET /version`
* `GET /quadrants/{criticality}/{complexity}`

---

# Flujo de procesamiento

```text
performance.yaml
        +
parametricConfigurationValues.yaml
        +
global_stats.json
        |
        v
Infrastructure Parsers
        |
        v
NormalizeExecution
        |
        v
ExecutionMetrics
        |
        v
Normalized JSON
```

---

# Calidad del proyecto

Ejecutar las verificaciones:

```powershell
ruff check .

black --check .

mypy src

pytest -v

pytest --cov=performance_decision_engine
```

Resultado esperado:

```text
All checks passed!

Success: no issues found

21 passed
```

---

# Hitos implementados

| Hito | Estado | Descripción       |
| ---- | :----: | ----------------- |
| H1   |    ✅   | Project Bootstrap |
| H2   |    ✅   | Parameter Values  |
| H3   |    ✅   | Performance YAML  |
| H4   |    ✅   | Gatling Results   |

---

# H4 – Gatling Results

El cuarto hito incorpora el parser oficial de resultados Gatling y normaliza la información para que el dominio permanezca completamente desacoplado del formato de la herramienta.

## Funcionalidades

* Lectura de `global_stats.json`
* Lectura opcional de `assertions.json`
* Validación de archivos JSON
* Validación de estructura
* Validación de requests
* Cálculo de Error Rate
* Extracción de Throughput
* Extracción de tiempos de respuesta
* Extracción de percentiles P50, P75, P95 y P99
* Normalización de assertions
* Entidades Pydantic tipadas
* Compatibilidad con Ruff
* Compatibilidad con MyPy
* Pruebas unitarias

## Componentes incorporados

* `ExecutionMetrics`
* `AssertionResult`
* `AssertionSummary`
* `GatlingMetricsReader`
* `GatlingAssertionsReader`

## Validaciones

El parser rechaza automáticamente:

* Archivos inexistentes
* JSON inválido
* Estructuras incompatibles
* Valores negativos
* Requests inconsistentes
* Assertions sin estado válido

---

# Roadmap

| Hito                    | Estado |
| ----------------------- | :----: |
| H5 – Normalization      |    ⏳   |
| H6 – Decision Matrix    |    ⏳   |
| H7 – Dataset Generation |    ⏳   |
| H8 – Machine Learning   |    ⏳   |
| H9 – Explainability     |    ⏳   |
| H10 – Integration       |    ⏳   |

---

# Estado actual

El proyecto incorpora actualmente:

* ✅ Arquitectura Clean Architecture
* ✅ Dominio desacoplado
* ✅ CLI funcional
* ✅ API REST
* ✅ Parser de `performance.yaml`
* ✅ Parser de `parametricConfigurationValues.yaml`
* ✅ Parser de resultados Gatling
* ✅ Normalización de métricas
* ✅ Persistencia JSON
* ✅ Baseline simple
* ✅ Pruebas unitarias
* ✅ Ruff
* ✅ MyPy
* ✅ Ejemplos funcionales

## Próximo objetivo

**H5 – Normalization**

Este hito unificará la configuración de la prueba (`PerformanceConfiguration`) con las métricas normalizadas (`ExecutionMetrics`) para construir una representación única de cada ejecución, que servirá posteriormente como base para la generación automática de datasets y el motor de recomendaciones basado en Machine Learning.
