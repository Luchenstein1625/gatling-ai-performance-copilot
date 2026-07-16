# 🚀 Gatling AI Performance Copilot

> Sistema inteligente y explicable para apoyar decisiones en pruebas de rendimiento.

![Status](https://img.shields.io/badge/status-H10%20Local%20PoC%20Completed-brightgreen)
![Capstone](https://img.shields.io/badge/UAI-Capstone-red)
![Python](https://img.shields.io/badge/Python-3.11%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Proyecto

**Gatling AI Performance Copilot** es un proyecto de Capstone del Magíster en Inteligencia Artificial de la Universidad Adolfo Ibáñez.

El proyecto implementa un **Performance Decision Engine** capaz de:

- interpretar configuraciones de pruebas;
- resolver parámetros corporativos;
- normalizar resultados Gatling;
- producir recomendaciones determinísticas;
- generar datasets reproducibles;
- entrenar un baseline supervisado;
- explicar reglas y modelos;
- ejecutar el flujo completo mediante una PoC local.

El caso de estudio utiliza Gatling, pero el dominio permanece desacoplado y puede admitir adaptadores para JMeter, k6, LoadRunner, NeoLoad u otras fuentes.

---

## Equipo

| Integrante | Rol |
|---|---|
| Luis Araya | Performance Engineering / IA |
| Rodrigo González | Desarrollo |
| Hernán Medina | Investigación |

**Profesor guía:** Ahmad Armoush  
**Universidad:** Universidad Adolfo Ibáñez

---

## Arquitectura

El proyecto sigue principios de Clean Architecture, Domain Driven Design, SOLID e inversión de dependencias.

```text
Interfaces
    │
    ▼
Application
    │
    ▼
Domain
    ▲
    │
Infrastructure
```

El dominio no depende de Gatling, YAML, JSON, Typer, FastAPI, scikit-learn ni mecanismos concretos de persistencia.

---

## Flujo funcional H1–H10

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
        ▼
RecommendExecution
        │
        ▼
Recommendation
        │
        ▼
GenerateDatasetRow
        │
        ▼
dataset.csv
        │
        ├──► TrainModel (opcional)
        │          │
        │          ▼
        │     model.joblib
        │          │
        │          ▼
        │     ExplainModel
        │
        ▼
pipeline_summary.json
        +
report.html
```

---

## Estado de los hitos

| Hito | Nombre | Estado |
|---|---|:---:|
| H1 | Project Bootstrap | ✅ |
| H2 | Parameter Values | ✅ |
| H3 | Performance YAML | ✅ |
| H4 | Gatling Results | ✅ |
| H5 | Normalization | ✅ |
| H6 | Decision Matrix | ✅ |
| H7 | Dataset Generation | ✅ |
| H8 | Machine Learning | ✅ |
| H9 | Explainability | ✅ |
| H10 | Local End-to-End Integration PoC | ✅ |

---

## Componentes implementados

### Configuración y métricas

- parser de `performance.yaml`;
- parser de `parametricConfigurationValues.yaml`;
- resolución de tripletas;
- parser de `global_stats.json`;
- parser opcional de `assertions.json`;
- métricas y percentiles normalizados.

### Decisión y explicabilidad

- `NormalizedExecution`;
- `RecommendExecution`;
- baseline determinístico;
- `decision_trace`;
- `triggered_rule`;
- explicación global del árbol H8.

### Datos y Machine Learning

- `GenerateDatasetRow`;
- dataset CSV versionado;
- importación histórica;
- `TrainModel`;
- `DecisionTreeClassifier`;
- validación de filas y clases;
- artefactos y reportes reproducibles.

### Integración H10

- `RunPipeline`;
- comando `pde pipeline`;
- persistencia de artefactos;
- reporte HTML autocontenido;
- entrenamiento y explicación opcionales;
- registro explícito de etapas omitidas;
- operación completamente local.

---

## Instalación

Desde `app`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

---

## Uso H10

```powershell
pde pipeline `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output-dir examples/output/pipeline
```

Con entrenamiento opcional:

```powershell
pde pipeline `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output-dir examples/output/pipeline `
  --train
```

---

## Salidas H10

```text
execution_summary.json
recommendation.json
dataset.csv
pipeline_summary.json
report.html
```

Condicionalmente:

```text
model.joblib
training_report.json
model_explanation.json
```

---

## Calidad

```powershell
black --check .
ruff check .
mypy src
pytest -v
```

---

## Alcance de la PoC

H10 es una PoC local. No integra:

- Azure DevOps;
- AKS;
- APIM;
- secretos corporativos;
- autenticación corporativa;
- ejecución remota de Gatling;
- datos productivos;
- plataformas internas del banco.

Las integraciones futuras deberán implementarse mediante adaptadores, sin modificar el dominio.

---

## Licencia

MIT License.

---

## Proyecto académico

Magíster en Inteligencia Artificial  
Universidad Adolfo Ibáñez  
2026
