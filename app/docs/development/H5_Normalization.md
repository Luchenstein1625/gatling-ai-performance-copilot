# H5 – Normalization

## Objetivo

El objetivo del Hito 5 es construir un proceso de normalización capaz de transformar la información proveniente de diferentes fuentes de una ejecución de pruebas de rendimiento en una representación única, consistente e independiente de la herramienta de origen.

Este proceso constituye la base para los siguientes hitos del proyecto, especialmente el motor de recomendación (H6), ya que entrega un modelo uniforme sobre el cual podrán aplicarse reglas de negocio y algoritmos de inteligencia artificial.

---

# Alcance

Durante este hito se implementó la normalización completa de una ejecución de pruebas de rendimiento considerando:

- Configuración de la prueba.
- Parámetros resueltos.
- Resultados globales de Gatling.
- Assertions (opcional).
- Validaciones de consistencia.
- Generación de un objeto único de dominio.

---

# Entradas

Actualmente el proceso soporta las siguientes entradas.

## Configuración

```
performance.yaml
```

Contiene:

- Endpoints
- Tripletas
- Configuración de carga
- Razones de ejecución
- Estado de cada endpoint

---

## Parámetros

```
parametricConfigurationValues.yaml
```

Contiene la resolución de niveles simbólicos como:

```
low
medium
high
```

hacia valores numéricos reales.

---

## Métricas

```
global_stats.json
```

Generado por Gatling.

Incluye:

- Requests
- TPS
- Percentiles
- Response Times
- Error Rate

---

## Assertions (Opcional)

```
assertions.json
```

Permite incorporar el resultado de las validaciones ejecutadas por Gatling.

---

# Salida

El proceso produce una instancia de:

```
NormalizedExecution
```

La cual contiene:

```
PerformanceConfiguration

ExecutionMetrics

Warnings
```

Este modelo representa una ejecución completamente normalizada y desacoplada de cualquier herramienta específica.

---

# Componentes implementados

## 1. Normalización de configuración

Se implementó:

- lectura de performance.yaml
- resolución automática de parámetros
- normalización de texto
- normalización de booleanos
- validación de datos faltantes
- conversión segura de tipos

---

## 2. Resolución de parámetros

Los niveles simbólicos son reemplazados automáticamente por valores numéricos.

Ejemplo:

```
medium
```

↓

```
20 usuarios
```

o

```
2000 ms
```

según corresponda.

---

## 3. Normalización de métricas

Se implementó soporte para:

- Total Requests
- Successful Requests
- Failed Requests
- Error Rate
- Requests per Second
- Minimum Response Time
- Mean Response Time
- Maximum Response Time
- Percentiles
- Assertions

---

## 4. Validaciones

Durante el proceso se validan automáticamente:

### Requests

- total = successful + failed

---

### Error Rate

Consistencia entre:

- requests fallidos
- requests totales
- porcentaje calculado

---

### Tipos

Validación de:

- enteros
- flotantes
- booleanos
- texto

---

### Valores

Se rechazan automáticamente:

- negativos
- NaN
- infinitos
- tipos inválidos

---

## 5. Manejo de Warnings

Los problemas que no impiden la normalización se almacenan como advertencias.

Ejemplos:

- endpoint sin parámetros
- endpoint deshabilitado
- tripleta incompleta
- ejecución sin requests

---

# Flujo

```
performance.yaml
            │

parametricConfigurationValues.yaml
            │

global_stats.json
            │

assertions.json
            │

────────────▼────────────

YamlConfigurationReader

GatlingMetricsReader

────────────▼────────────

NormalizeExecution

────────────▼────────────

NormalizedExecution
```

---

# Arquitectura

El caso de uso mantiene la separación propuesta por Clean Architecture.

```
Interfaces

↓

Application

↓

Domain

↑

Infrastructure
```

El dominio continúa siendo completamente independiente de:

- YAML
- JSON
- Gatling
- FastAPI
- CLI
- Persistencia

---

# Resultado

Al finalizar H5 el sistema dispone de un modelo único para representar cualquier ejecución de pruebas de rendimiento.

Este modelo será utilizado directamente por:

- Recommendation Engine
- Explainability
- Machine Learning
- API REST
- Dashboard

---

# Calidad

El desarrollo fue validado mediante:

## Formato

✔ Black

---

## Linter

✔ Ruff

---

## Tipado

✔ MyPy

---

## Pruebas

✔ Pytest

45 pruebas aprobadas.

---

# Definition of Done

El Hito 5 se considera completado cuando:

- La configuración se normaliza correctamente.
- Los parámetros se resuelven automáticamente.
- Las métricas Gatling se convierten al modelo interno.
- Las assertions pueden incorporarse opcionalmente.
- Se detectan inconsistencias automáticamente.
- Se generan warnings cuando corresponde.
- Se obtiene un objeto `NormalizedExecution`.
- Todas las pruebas automáticas son exitosas.
- Black, Ruff y MyPy no reportan errores.

---

# Estado

**Milestone:** H5

**Estado:** ✅ Completado

**Versión:** 0.3.0

**Próximo hito:** H6 – Recommendation Engine