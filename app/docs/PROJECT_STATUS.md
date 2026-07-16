# Project Status

## General Information

**Project:** Performance Decision Engine  
**Capstone:** Gatling AI Performance Copilot  
**University:** Universidad Adolfo Ibáñez  
**Program:** Magíster en Inteligencia Artificial

**Declared project version:**

```text
0.4.0
```

> Nota: `pyproject.toml` mantiene actualmente la versión de paquete `0.3.0`. Este documento no modifica código ni versionado.

**Current Milestone:**

```text
✅ H8 — Machine Learning implementation completed
```

**Next Milestone:**

```text
⏳ H9 — Explainability
```

---

# Executive Summary

The first eight roadmap milestones have reached their planned implementation state.

The application currently supports:

- performance configuration parsing;
- corporate parameter resolution;
- Gatling metrics parsing;
- optional assertions parsing;
- execution normalization;
- deterministic recommendations;
- stable dataset-row generation;
- historical batch execution discovery;
- historical dataset import;
- dataset validation;
- supervised-learning orchestration;
- Decision Tree training through an infrastructure backend;
- explicit rejection of non-trainable datasets;
- CLI and REST interfaces.

H8 is technically implemented. Model training cannot currently be executed against the available historical dataset because the target contains only one class.

This is a historical-data limitation, not an implementation defect.

---

# Milestone Status

| Milestone | Description | Status |
|---|---|---|
| H1 | Project Structure | ✅ Completed |
| H2 | YAML Configuration Parser | ✅ Completed |
| H3 | Parameter Resolution | ✅ Completed |
| H4 | Gatling Metrics Parser | ✅ Completed |
| H5 | Normalization | ✅ Completed |
| H6 | Decision Matrix | ✅ Completed |
| H7 | Dataset Generation | ✅ Completed |
| H8 | Machine Learning | ✅ Implementation completed |
| H9 | Explainability | ⏳ Next |
| H10 | Integration | ⏳ Planned |

---

# Current Capabilities

## Architecture

- Clean Architecture
- Domain Driven Design
- SOLID
- Strong typing
- Dependency inversion
- Framework-independent domain

## Configuration and Metrics

- YAML Parser
- Parameter Resolution
- Endpoint and triplet normalization
- Gatling Metrics Parser
- Optional Assertions Parser
- Error Rate
- Percentiles
- TPS
- Response Times

## Domain and Application

- Quadrant Resolution
- `NormalizeExecution`
- `NormalizedExecution`
- `RecommendExecution`
- `Recommendation`
- `GenerateDatasetRow`
- `TrainModel`

## Infrastructure

- external-format parsers;
- JSON persistence;
- historical execution discovery;
- Decision Tree training backend;
- model artifact persistence through the implemented backend.

## Interfaces

- CLI
- REST API

---

# H6 Deliverables — Decision Matrix

H6 provides the deterministic recommendation baseline.

```text
NormalizedExecution
        │
        ▼
RecommendExecution
        │
        ▼
Recommendation
```

The deterministic decision remains active and is not replaced by H8.

---

# H7 Deliverables — Dataset Generation

H7 provides a stable, versioned dataset contract.

```text
NormalizedExecution
        +
Recommendation
        │
        ▼
GenerateDatasetRow
        │
        ▼
CSV schema version 1
```

Guarantees:

- one real execution produces one row;
- the H6 action is stored in `recommendation_action`;
- metrics retain execution-level scope;
- missing values remain missing;
- CSV headers are validated;
- no unsupported attributes are invented.

Historical-import interpretation:

- each dated directory represents exactly one execution;
- multiple Gatling files inside that directory belong to the same execution;
- contained files must not be counted as additional executions.

---

# H8 Deliverables — Machine Learning

H8 introduces the supervised-learning implementation while preserving the existing architecture.

## Application

- `TrainModel` orchestrates the training use case.
- Application logic remains separated from the concrete Machine Learning backend.

## Infrastructure

- historical execution discovery;
- batch dataset import support;
- Decision Tree training backend;
- model artifact persistence using the H8 infrastructure implementation.

## Validation

The implementation rejects training when:

- the dataset is incompatible;
- required information is unavailable;
- there are not enough valid examples;
- the target contains a single class.

## Compatibility

- H6 remains the deterministic baseline.
- H7 remains the dataset contract.
- No synthetic data are generated.
- H1–H7 public behavior remains compatible.

---

# Historical Dataset Status

The current historical dataset contains:

| Measure | Value |
|---|---:|
| Real historical executions | 11 |
| `maintain` | 11 |
| `review` | 0 |
| Target classes | 1 |

The historical importer and `dataset-batch` workflow operate correctly.

Training cannot currently proceed because supervised classification requires more than one target class. The implementation correctly detects and reports this condition.

No synthetic executions will be added to bypass the limitation.

New real executions containing errors are expected to provide future `review` examples.

---

# Current Constraints

- Metrics remain execution-scoped.
- Endpoint-level metrics are not represented in the current normalized model.
- Deterministic recommendations are execution-wide.
- The historical dataset contains only one target class.
- No valid trained-model performance metrics can be reported yet.

These constraints must remain visible in project documentation.

---

# Quality Gates

Every change must pass:

```powershell
black --check .
ruff check .
mypy src
pytest
```

Current status:

- ✅ Black
- ✅ Ruff
- ✅ MyPy
- ✅ Pytest

---

# Automated Tests

Current automated test suite:

```text
61 passing tests
```

Coverage includes:

- YAML Parser
- Parameter Resolution
- Gatling Parser
- Assertions Parser
- Normalization
- Recommendation Engine
- Quadrant Resolution
- Dataset Generation
- Historical Execution Discovery
- Decision Tree Training Backend
- TrainModel
- CLI
- Validation Rules

---

# Architecture Compatibility

The project continues following the existing dependency direction:

```text
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

The domain remains independent from:

- Gatling;
- YAML;
- JSON;
- FastAPI;
- CLI;
- persistence;
- scikit-learn;
- joblib.

Machine Learning dependencies remain outside the domain.

---

# Next Milestone

## H9 — Explainability

H9 is the next roadmap milestone.

Its architecture must be proposed only after a complete review of the existing implementation and must preserve compatibility with H1–H8.

No H9 implementation is included in this documentation update.

---

# Project Status

🟢 Active Development

Last completed implementation milestone:

```text
✅ H8 — Machine Learning
```

Next milestone:

```text
⏳ H9 — Explainability
```
