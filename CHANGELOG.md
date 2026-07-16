# Changelog

Los cambios relevantes del proyecto se documentan en este archivo.

## [0.10.0] - 2026-07-16

### H10 — Local End-to-End Integration PoC

#### Agregado

- caso de uso `RunPipeline`;
- comando `pde pipeline`;
- generación de `execution_summary.json`;
- generación de `recommendation.json`;
- actualización incremental de `dataset.csv`;
- generación de `pipeline_summary.json`;
- reporte HTML autocontenido;
- entrenamiento H8 opcional;
- explicación H9 opcional;
- registro controlado de entrenamiento omitido;
- pruebas del pipeline integrado;
- pruebas de generación y escape del reporte HTML.

#### Alcance

La integración es una PoC completamente local y no se conecta con plataformas del banco.

## [0.9.0] - 2026-07-16

### H9 — Explainability

- traza estructurada de reglas;
- `triggered_rule`;
- caso de uso `ExplainModel`;
- explicación global de modelos H8;
- importancia de variables;
- reglas textuales;
- validación de artefactos.

## [0.8.0] - 2026-07-16

### H8 — Machine Learning

- caso de uso `TrainModel`;
- baseline `DecisionTreeClassifier`;
- validación de dataset;
- persistencia de modelo;
- reporte de entrenamiento;
- rechazo seguro de datasets insuficientes o de una sola clase.

## [0.7.0] - 2026-07-16

### H7 — Dataset Generation

- `GenerateDatasetRow`;
- comando `pde dataset`;
- esquema CSV versionado;
- etiqueta `recommendation_action`;
- validación de encabezados;
- importación histórica.

## [0.6.0]

### H6 — Decision Matrix

- Recommendation Engine determinístico;
- reglas de error rate, P95, assertions, requests y endpoints;
- entidad `Recommendation`;
- explicación y evidencia.

## [0.5.0]

### H5 — Normalization

- `NormalizeExecution`;
- `NormalizedExecution`;
- combinación de configuración y métricas.

## [0.4.0]

### H4 — Gatling Results

- lectura de `global_stats.json`;
- assertions opcionales;
- métricas y percentiles.

## [0.3.0]

### H3 — Performance YAML

- interpretación de configuración de rendimiento;
- endpoints y tripletas.

## [0.2.0]

### H2 — Parameter Values

- resolución de niveles semánticos;
- validación de parámetros.

## [0.1.0]

### H1 — Project Bootstrap

- estructura inicial;
- arquitectura limpia;
- paquete Python;
- CLI y API mínimas;
- configuración de calidad.
