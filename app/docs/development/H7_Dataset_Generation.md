# H7 — Dataset Generation

## Estado

✅ Completado

## Objetivo

Transformar una ejecución normalizada y la decisión determinística de H6 en una fila estable, reproducible y preparada para Machine Learning.

---

# Diseño

H7 reutiliza:

- `NormalizedExecution`;
- `Recommendation`;
- `RecommendExecution`;
- `GenerateDatasetRow`;
- la interfaz CLI existente.

No introduce entidades, Value Objects, DTO, repositorios ni dependencias de Machine Learning dentro del dominio.

---

# Flujo

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

---

# Contrato del dataset

- Una ejecución equivale a una fila.
- `schema_version` identifica el contrato.
- `metrics_scope` permanece en `execution`.
- `recommendation_action` es la etiqueta generada por H6.
- Los valores ausentes se mantienen como valores ausentes.
- No se inventan criticidad, complejidad ni cuadrantes.
- El encabezado existente se valida antes de anexar una fila.

---

# Regla para importación histórica

Una carpeta con fecha corresponde exactamente a **una ejecución real**.

Ejemplo:

```text
ms-loyalty-ofertas/
├── 20260623/
├── 20260702/
└── 20260703/
```

El ejemplo anterior representa tres ejecuciones.

Los múltiples archivos Gatling contenidos dentro de cada carpeta fechada pertenecen a esa ejecución y no representan ejecuciones adicionales.

---

# Archivos de H7

## Nuevos

- `application/use_cases/generate_dataset.py`
- `tests/test_generate_dataset.py`
- `docs/development/H7_Dataset_Generation.md`

## Modificados

- `interfaces/cli/main.py`
- documentación de estado y roadmap

---

# Pruebas al cierre de H7

H7 agregó pruebas para:

- generación estable de una fila;
- agregaciones incompletas;
- assertions opcionales;
- validación del encabezado del dataset.

Estado al cierre original de H7:

- Black ✅
- Ruff ✅
- MyPy ✅
- Pytest ✅
- 53 pruebas aprobadas

Estado acumulado después de H8:

- Black ✅
- Ruff ✅
- MyPy ✅
- Pytest ✅
- 61 pruebas aprobadas

---

# Consumo real por H8

H8 consume el contrato generado por H7 sin modificar su significado.

La implementación H8 agregó:

- descubrimiento de ejecuciones históricas;
- importación por lotes;
- validación previa al entrenamiento;
- caso de uso `TrainModel`;
- backend de entrenamiento basado en Decision Tree.

H7 permanece como contrato de entrada para Machine Learning.

---

# Estado real del dataset histórico

Actualmente existen:

| Métrica | Valor |
|---|---:|
| Ejecuciones históricas reales | 11 |
| `maintain` | 11 |
| `review` | 0 |

El importador histórico y `dataset-batch` funcionan correctamente.

El dataset contiene una sola clase, por lo que H8 rechaza correctamente el entrenamiento supervisado.

Esta condición no representa un error de H7 ni de H8. Es una limitación del histórico real disponible.

No se generarán datasets sintéticos para ocultarla.

---

# Riesgos conocidos

- Las métricas siguen siendo globales.
- La etiqueta H6 es determinística.
- El histórico contiene actualmente una sola clase.
- Todavía no es posible reportar métricas de un modelo entrenado.
- Los archivos individuales dentro de una ejecución no deben contarse como ejecuciones adicionales.

---

# Compatibilidad

H1–H6 permanecen compatibles.

H8 consume el dataset H7 sin modificar:

- `NormalizedExecution`;
- `Recommendation`;
- el esquema CSV versionado;
- el comportamiento público previo.

---

# Definition of Done

- ✅ El esquema es estable y versionado.
- ✅ La fila sólo utiliza datos existentes.
- ✅ La etiqueta proviene de H6.
- ✅ El CSV valida su encabezado.
- ✅ La importación histórica respeta una carpeta fechada por ejecución.
- ✅ Los Quality Gates aprueban.
- ✅ H8 consume el dataset sin modificar H5–H7.
- ✅ La limitación de una sola clase queda documentada.
