# Project Status

## General Information

**Project:** Performance Decision Engine

**Capstone:** Gatling AI Performance Copilot

**University:** Universidad Adolfo Ibáñez

**Program:** Magíster en Inteligencia Artificial

**Current Version**

```
0.4.0
```

**Current Milestone**

✅ H6 – Decision Matrix

---

# Executive Summary

The project has successfully completed the first six milestones defined in the roadmap.

The application is now capable of:

- parsing performance configurations;
- resolving corporate parameters;
- parsing Gatling execution metrics;
- parsing optional assertions;
- normalizing complete executions;
- generating baseline recommendations;
- exposing functionality through CLI and REST API.

The application remains fully aligned with:

- Clean Architecture
- Domain Driven Design
- SOLID Principles

---

# Milestone Status

| Milestone | Description | Status |
|-----------|-------------|--------|
| H1 | Project Structure | ✅ Completed |
| H2 | YAML Configuration Parser | ✅ Completed |
| H3 | Parameter Resolution | ✅ Completed |
| H4 | Gatling Metrics Parser | ✅ Completed |
| H5 | Normalization | ✅ Completed |
| H6 | Decision Matrix | ✅ Completed |
| H7 | Dataset Generation | ⏳ Planned |
| H8 | Machine Learning | ⏳ Planned |
| H9 | Explainability | ⏳ Planned |
| H10 | Integration | ⏳ Planned | Machine Learning | ⏳ Planned |

---

# Current Capabilities

The project currently implements:

## Architecture

- Clean Architecture
- Domain Driven Design
- SOLID
- Strong typing
- Dependency inversion

---

## Configuration

- YAML Parser
- Parameter Resolution
- Endpoint normalization
- Triplet normalization

---

## Metrics

- Gatling Metrics Parser
- Optional Assertions Parser
- Error Rate
- Percentiles
- TPS
- Response Times

---

## Domain

- Quadrant Resolution
- NormalizeExecution
- NormalizedExecution
- Recommendation Engine

---

## Persistence

- JSON Repository

---

## Interfaces

- CLI
- REST API

---

# H5 Deliverables

The following functionality was completed during H5.

## Configuration Normalization

The engine now resolves:

- symbolic configuration values;
- endpoint metadata;
- triplet values;
- logical levels;
- boolean values.

The resulting configuration is represented through a single normalized model.

---

## Metrics Normalization

Execution metrics include:

- total requests;
- successful requests;
- failed requests;
- error rate;
- minimum response time;
- mean response time;
- maximum response time;
- percentiles;
- TPS;
- optional assertions.

---

## Output

The normalization process generates a canonical domain object:

```
NormalizedExecution
```

This object is now the only input required by the Recommendation Engine.

---

# H6 Deliverables — Decision Matrix

The Recommendation Engine introduces automatic evaluation of normalized executions.

The recommendation process is completely independent from:

- YAML;
- Gatling;
- CLI;
- REST API;
- persistence.

---

## Recommendation Flow

```
NormalizedExecution
        │
        ▼
RecommendExecution
        │
        ▼
Recommendation
```

---

## Recommendation Rules

### Error Rate

If failed requests exist:

```
review
```

---

### Response Time

If:

```
P95 > configured target
```

↓

```
review
```

---

### Assertions

If assertions exist and at least one fails:

```
review
```

---

### Empty Execution

If:

```
requests == 0
```

↓

```
review
```

---

### Missing Endpoints

If no enabled endpoints exist:

```
review
```

---

### Successful Execution

If every previous validation succeeds:

```
maintain
```

---

# Recommendation Output

The Recommendation Engine generates:

```text
Recommendation
├── action
├── explanation
└── evidence
```

Evidence contains:

- error rate;
- P95;
- configured response time target;
- request counters;
- enabled endpoints;
- warnings;
- metrics scope.

---

# Current Constraints

The current implementation intentionally evaluates only execution-level metrics.

Therefore:

- metrics are global;
- endpoint metrics are not yet available;
- recommendations are generated for the complete execution.

This limitation will be addressed during future milestones.

---

# Quality Gates

Every commit must successfully pass:

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

**50 passing tests**

Coverage includes:

- YAML Parser
- Parameter Resolution
- Gatling Parser
- Assertions Parser
- Normalization
- Recommendation Engine
- Quadrant Resolution
- CLI
- Validation Rules

---

# Architecture

The project continues following the same architecture.

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

The domain remains independent from:

- Gatling;
- YAML;
- JSON;
- FastAPI;
- CLI;
- persistence.

---

# Next Milestone

## H7 – Dataset Generation

Objectives:

- generate reproducible records from `NormalizedExecution`;
- include the deterministic H6 decision as the target;
- define a stable dataset schema;
- validate completeness and consistency;
- prepare the supervised-learning input for H8.

---

# Future Milestones

## H8 – Machine Learning

- supervised learning;
- historical execution datasets;
- intelligent recommendation models;
- prediction;
- confidence estimation.

## H9 – Explainability

- rule and model explanation;
- decision traceability;
- enriched evidence;
- recommendation auditing.

## H10 – Integration

- end-to-end integration;
- operational interfaces;
- final compatibility validation.

---

# Project Status

🟢 Active Development

Current milestone:

✅ H6 Completed

Next milestone:

⏳ H7 Explainability