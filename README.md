# 🚀 Gatling AI Performance Copilot

> Sistema Inteligente para la recomendación y automatización de pruebas de rendimiento mediante Inteligencia Artificial.

![Status](https://img.shields.io/badge/status-H6%20Completed-brightgreen)
![Capstone](https://img.shields.io/badge/UAI-Capstone-red)
![Python](https://img.shields.io/badge/Python-3.12-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

# 📖 Proyecto

**Gatling AI Performance Copilot** es el proyecto de Capstone del **Magíster en Inteligencia Artificial de la Universidad Adolfo Ibáñez (UAI)**.

El proyecto tiene como objetivo desarrollar un sistema inteligente capaz de asistir a especialistas de QA y Performance Engineering durante el diseño, configuración, análisis y evolución de pruebas de rendimiento.

A diferencia de herramientas tradicionales, el proyecto busca transformar un proceso principalmente manual en un proceso:

- Explicable
- Reproducible
- Basado en evidencia
- Preparado para Inteligencia Artificial

El caso de estudio inicial utiliza **Gatling**, pero la arquitectura fue diseñada para permitir la incorporación de otras herramientas de pruebas de rendimiento como:

- JMeter
- k6
- LoadRunner
- NeoLoad
- Herramientas propietarias

sin modificar el dominio de la aplicación.

---

# 🎯 Objetivo General

Diseñar e implementar un **Performance Decision Engine** capaz de:

- interpretar configuraciones de pruebas;
- resolver parámetros corporativos;
- normalizar ejecuciones;
- analizar métricas;
- generar recomendaciones automáticas;
- evolucionar posteriormente hacia Machine Learning y Explainable AI.

---

# 🎯 Objetivos Específicos

Durante el desarrollo del proyecto se busca implementar progresivamente:

- Parser de configuraciones YAML.
- Resolución de parámetros simbólicos.
- Parser de resultados Gatling.
- Normalización completa de una ejecución.
- Recommendation Engine.
- Explainability.
- Machine Learning.
- Dashboard de apoyo para especialistas.

---

# 👥 Equipo

| Integrante | Rol |
|------------|-----|
| Luis Araya | Performance Engineering / IA |
| Rodrigo González | Desarrollo |
| Hernán Medina | Investigación |

### Profesor Guía

**Ahmad Armoush**

Universidad Adolfo Ibáñez

---

# 🏗 Arquitectura del repositorio

```

gatling-ai-performance-copilot

│

├── AI_CONTEXT/
├── app/
├── DATA/
├── DECISIONS/
├── DEFENSE/
├── EVALUATION/
├── KNOWLEDGE/
├── MAGISTER/
├── MEETINGS/
├── PLANNING/
├── PRESENTATIONS/
├── PROJECT/
├── PROMPTS/
├── RESEARCH/
├── RESOURCES/
├── TEMPLATES/

├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE.md
└── README.md

```

---

# 📂 Organización del repositorio

| Carpeta | Descripción |
|----------|-------------|
| PROJECT | Documentación principal del proyecto |
| app | Implementación del sistema |
| DATA | Dataset y calidad de datos |
| EVALUATION | Protocolos de evaluación |
| DECISIONS | Architecture Decision Records |
| KNOWLEDGE | Base documental |
| PRESENTATIONS | Presentaciones |
| MAGISTER | Material académico |
| DEFENSE | Material para defensa |

---

# 🧠 Arquitectura de la solución

El sistema sigue los principios de **Clean Architecture** y **Domain Driven Design**.

La aplicación se divide en cuatro capas principales:

```
Interfaces
        │
        ▼
Application
        │
        ▼
Domain
        ▲
Infrastructure
```

## Principios

- Bajo acoplamiento.
- Alta cohesión.
- Inversión de dependencias.
- Dominio independiente de frameworks.
- Casos de uso desacoplados.
- Adaptadores para herramientas externas.

---

# 🔄 Flujo funcional

El flujo implementado actualmente corresponde a los hitos H1–H6.

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

El modelo `NormalizedExecution` constituye la representación canónica de una ejecución de pruebas de rendimiento dentro del dominio.

A partir de H6, el Recommendation Engine consume este modelo para producir una recomendación basada en reglas determinísticas.

---

# 🧩 Componentes implementados

Actualmente el proyecto implementa los siguientes componentes funcionales:

## Configuración

- YAML Configuration Parser
- Parameter Resolver
- Performance Configuration Model
- Endpoint Configuration
- Triplet Resolution

## Métricas

- Gatling Metrics Parser
- Assertions Parser (opcional)
- Execution Metrics
- Percentiles
- Error Rate
- Requests per Second (TPS)

## Dominio

- Quadrant Resolution
- NormalizeExecution
- NormalizedExecution
- Recommendation Engine (Baseline)

## Interfaces

- CLI (`pde`)
- REST API

## Persistencia

- JSON Repository

---

# 📊 Estado del proyecto

## Roadmap

| Hito | Descripción | Estado |
|------|-------------|--------|
| H1 | Estructura del proyecto | ✅ |
| H2 | YAML Configuration Parser | ✅ |
| H3 | Parameter Resolution | ✅ |
| H4 | Gatling Metrics Parser | ✅ |
| H5 | Normalization Engine | ✅ |
| H6 | Recommendation Engine | ✅ |
| H7 | Explainability | ⏳ |
| H8 | Machine Learning | ⏳ |

---

# ✅ Funcionalidades implementadas

Hasta el H6 el sistema permite:

- Leer configuraciones de rendimiento.
- Resolver parámetros corporativos.
- Leer resultados de Gatling.
- Leer assertions (opcionalmente).
- Resolver cuadrantes.
- Normalizar configuraciones.
- Normalizar métricas.
- Construir un `NormalizedExecution`.
- Generar recomendaciones baseline.
- Persistir resultados en JSON.
- Exponer funcionalidad mediante CLI.
- Exponer funcionalidad mediante REST API.

---

# 🚀 Recommendation Engine (H6)

El Recommendation Engine constituye el primer motor de decisión del proyecto.

Su objetivo consiste en transformar una ejecución normalizada en una recomendación reutilizable por cualquier consumidor del dominio.

## Entrada

El motor recibe exclusivamente un objeto:

```text
NormalizedExecution
```

No depende de:

- Gatling
- YAML
- JSON
- CLI
- FastAPI

Esto permite que futuras implementaciones reutilicen exactamente el mismo caso de uso.

---

## Flujo interno

```text
NormalizedExecution
        │
        ▼
RecommendExecution
        │
        ▼
Recommendation
```

---

## Reglas baseline implementadas

Actualmente el Recommendation Engine implementa reglas determinísticas simples.

### Error Rate

Si la ejecución contiene solicitudes fallidas:

```text
error_rate > 0
```

↓

```text
review
```

---

### Tiempo de respuesta

Si el percentil P95 supera el objetivo configurado:

```text
p95 > response_time_target
```

↓

```text
review
```

---

### Assertions

Si existen assertions y alguna falla:

```text
failed assertions
```

↓

```text
review
```

---

### Ejecución vacía

Si la ejecución no contiene solicitudes:

```text
requests == 0
```

↓

```text
review
```

---

### Sin endpoints habilitados

Cuando no existen endpoints habilitados para evaluar:

```text
enabled_endpoints == 0
```

↓

```text
review
```

---

### Ejecución correcta

Cuando todas las reglas anteriores son satisfactorias:

```text
maintain
```

---

# 📦 Recommendation JSON

La salida corresponde a una entidad de dominio denominada:

```text
Recommendation
```

Ejemplo:

```json
{
  "action": "maintain",
  "explanation": "Las reglas básicas evaluadas no detectaron incumplimientos.",
  "evidence": {
    "error_rate_percent": 0.0,
    "p95_response_time_ms": 1465,
    "expected_response_time_ms": 15000,
    "total_requests": 2801,
    "successful_requests": 2801,
    "failed_requests": 0,
    "enabled_endpoints": [
      "buscar consentimiento"
    ],
    "metrics_scope": "execution"
  }
}
```

---

# ⚠ Limitaciones actuales

La versión H6 utiliza únicamente las métricas disponibles dentro de `NormalizedExecution`.

Actualmente:

- Las métricas corresponden a la ejecución completa.
- No existen métricas individuales por endpoint.
- Las recomendaciones son globales para toda la ejecución.

Estas limitaciones serán abordadas durante los hitos H7 y H8.

---

# 💻 Command Line Interface (CLI)

La aplicación expone una interfaz de línea de comandos mediante el ejecutable:

```text
pde
```

Los comandos disponibles al finalizar H6 son:

## Verificar instalación

```powershell
pde doctor
```

Permite validar:

- instalación correcta;
- dependencias;
- versión de Python;
- entorno de ejecución.

---

## Obtener versión

```powershell
pde --version
```

---

## Resolver cuadrantes

```powershell
pde quadrant `
    --criticality high `
    --complexity medium
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

Si existen assertions:

```powershell
pde normalize `
    --performance examples/input/performance.yaml `
    --parameters examples/input/parametricConfigurationValues.yaml `
    --results examples/input/global_stats.json `
    --assertions examples/input/assertions.json `
    --output examples/output/execution_summary.json
```

Salida:

```text
NormalizedExecution
```

---

## Recommendation Engine

El H6 incorpora un nuevo comando:

```powershell
pde recommend `
    --performance examples/input/performance.yaml `
    --parameters examples/input/parametricConfigurationValues.yaml `
    --results examples/input/global_stats.json `
    --output examples/output/recommendation.json
```

Ejemplo de salida:

```text
Recommendation: maintain

Las reglas básicas evaluadas no detectaron incumplimientos.

Created:
examples/output/recommendation.json
```

---

# 🌐 REST API

La aplicación expone una API REST implementada mediante FastAPI.

## Ejecutar

```powershell
uvicorn performance_decision_engine.interfaces.api.main:app --reload
```

---

## Endpoints disponibles

### Health Check

```
GET /health
```

Permite verificar que la aplicación se encuentra operativa.

---

### Version

```
GET /version
```

Devuelve la versión actual de la aplicación.

---

### Quadrants

```
GET /quadrants/{criticality}/{complexity}
```

Obtiene el cuadrante correspondiente según la matriz implementada.

---

### Recommendations (H6)

```
POST /recommendations
```

Entrada:

```text
NormalizedExecution
```

Salida:

```text
Recommendation
```

---

# 🧪 Calidad del proyecto

Todos los cambios incorporados al proyecto deben cumplir obligatoriamente los siguientes controles de calidad.

## Formato

```powershell
black --check .
```

---

## Estilo

```powershell
ruff check .
```

---

## Tipado

```powershell
mypy src
```

---

## Pruebas

```powershell
pytest
```

---

## Estado actual

Al finalizar el H6:

- ✅ Black
- ✅ Ruff
- ✅ MyPy
- ✅ Pytest

**50 pruebas automatizadas aprobadas.**

---

# 📈 Evolución del proyecto

La arquitectura fue diseñada para evolucionar progresivamente.

## H1

Estructura inicial del proyecto.

---

## H2

Parser YAML.

---

## H3

Resolución de parámetros.

---

## H4

Parser de métricas Gatling.

---

## H5

Normalización completa de una ejecución mediante `NormalizedExecution`.

---

## H6

Recommendation Engine basado en reglas determinísticas.

---

## Próximo Hito — H7

El objetivo del siguiente hito consiste en incorporar capacidades de Explainability.

Entre las funcionalidades esperadas se encuentran:

- explicación detallada de las recomendaciones;
- trazabilidad de reglas;
- evidencia estructurada;
- preparación para modelos de Machine Learning.

---

## H8

El último hito incorporará:

- modelos predictivos;
- entrenamiento supervisado;
- recomendación inteligente basada en ejecuciones históricas;
- Dashboard de apoyo para especialistas;
- integración completa con Explainable AI.

---

# 🤝 Contribuciones

Todas las nuevas funcionalidades deberán mantener los siguientes principios:

- Clean Architecture.
- Domain Driven Design.
- SOLID.
- Tipado estático.
- Cobertura mediante pruebas automatizadas.
- Compatibilidad hacia atrás.

No se aceptarán cambios que rompan funcionalidades previamente implementadas.

---

# 📄 Licencia

MIT License.

---

# 🎓 Proyecto Académico

Proyecto desarrollado como parte del:

**Magíster en Inteligencia Artificial**

Universidad Adolfo Ibáñez

2026

---

**Fin del README.md**


