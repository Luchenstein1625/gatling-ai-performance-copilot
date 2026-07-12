# H4 - Gatling Results

## Objetivo

Implementar la normalización de los resultados generados por Gatling para que puedan ser utilizados por el motor de decisión de forma independiente del formato original de la herramienta.

---

## Problema

Los reportes generados por Gatling contienen una gran cantidad de información, pero su estructura depende de la versión de Gatling y no debe propagarse al dominio del proyecto.

Este hito encapsula toda esa lógica mediante un parser especializado que transforma los archivos de Gatling en entidades del dominio.

---

## Entradas

* `global_stats.json`
* `assertions.json` (opcional)

---

## Salidas

* `ExecutionMetrics`
* `AssertionSummary`
* `AssertionResult`

---

## Funcionalidades implementadas

* Lectura de `global_stats.json`
* Lectura opcional de `assertions.json`
* Validación de existencia de archivos
* Validación de formato JSON
* Validación de estructura de métricas
* Validación de consistencia entre:

  * Requests Totales
  * Requests Exitosos
  * Requests Fallidos
* Cálculo del porcentaje de error
* Extracción de:

  * Requests
  * Throughput
  * Response Time
  * Percentiles P50
  * Percentiles P75
  * Percentiles P95
  * Percentiles P99
* Normalización de assertions
* Modelado mediante entidades Pydantic

---

## Componentes

```text
ExecutionMetrics
AssertionSummary
AssertionResult
GatlingMetricsReader
GatlingAssertionsReader
```

---

## Validaciones

El parser rechaza:

* Archivos inexistentes
* JSON inválido
* Estructuras incompatibles
* Valores negativos
* Requests inconsistentes
* Assertions sin estado válido

---

## Pruebas unitarias

Se incorporaron pruebas para:

* Lectura correcta de métricas
* Lectura correcta de assertions
* JSON inválido
* Archivo inexistente
* Requests inconsistentes
* Assertions inválidas
* Integración entre métricas y assertions

---

## Ejecución

Instalar dependencias:

```powershell
pip install -e ".[dev]"
```

Ejecutar pruebas:

```powershell
pytest -v
```

Validar Ruff:

```powershell
ruff check .
```

Validar MyPy:

```powershell
mypy src
```

---

## Resultado esperado

```text
ruff:
All checks passed!

mypy:
Success: no issues found

pytest:
21 passed
```

---

## Estado

✅ Completado

---

## Próximo hito

H5 - Normalization
