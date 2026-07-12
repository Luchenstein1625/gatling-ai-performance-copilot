# Gatling AI Performance Copilot

Repositorio oficial del Capstone del Magíster en Inteligencia Artificial de la Universidad Adolfo Ibáñez.

## Integrantes
- Luis Araya
- Rodrigo González
- Hernán Medina

## Profesor guía
Ahmad Armoush

## Visión
Automatizar la generación de pruebas Gatling mediante IA generativa y aprender del historial de cada microservicio para recomendar el cuadrante de prueba más adecuado.

## Uso del repositorio
Este repositorio es la fuente única de verdad del proyecto. Registra problema, objetivos, arquitectura, decisiones, reuniones, experimentos, papers, contenidos del Magíster, presentaciones y defensa.

## Próximo hito
Validar con el profesor guía el cambio de tema, la innovación, el acceso a datos, el alcance, la metodología y las métricas.

📖 Documentación
📅 Planificación
💻 Código
📊 Datos
📈 Evaluación
🎓 Material Magíster

# 🚀 Gatling AI Performance Copilot

> Sistema Inteligente de apoyo a la toma de decisiones para pruebas de rendimiento.

---

# 📖 Descripción

Gatling AI Performance Copilot es el proyecto de **Capstone del Magíster en Inteligencia Artificial** cuyo objetivo es asistir a los especialistas de QA Infraestructura en la selección del cuadrante más adecuado para ejecutar pruebas de rendimiento sobre microservicios.

El proyecto reutiliza:

- configuración actual (`performance.yaml`)
- parámetros corporativos (`parametricConfigurationValues.yaml`)
- resultados históricos de Gatling
- conocimiento experto
- matriz de decisión de nueve cuadrantes

para recomendar configuraciones de prueba explicables y trazables.

---

# 🎯 Objetivo del proyecto

Diseñar y validar un sistema inteligente que recomiende el cuadrante más adecuado para ejecutar una prueba de rendimiento, utilizando conocimiento experto, configuraciones reales y resultados históricos.

---

# 🗂 Estructura del repositorio

```
.
├── AI_CONTEXT/
├── DATA/
├── DECISIONS/
├── EVALUATION/
├── MAGISTER/
├── PLANNING/
├── PRESENTATIONS/
├── PROJECT/
├── RESOURCES/
├── scripts/
├── src/
└── README.md
```

---

# 📂 Descripción de cada carpeta

## 📁 PROJECT/

Contiene toda la definición académica y técnica del Capstone.

Incluye:

- definición del proyecto
- problema
- objetivos
- alcance
- metodología
- arquitectura
- Tripleta
- matriz de decisión
- migración de performance-lib

---

## 📁 PLANNING/

Contiene la planificación completa del proyecto.

Incluye:

- roadmap
- calendario
- hitos
- backlog
- planificación de la Presentación 2
- planificación de la presentación final

---

## 📁 PRESENTATIONS/

Material utilizado para las exposiciones del Magíster.

Incluye:

- estructura de las presentaciones
- checklist para la evaluación
- material de apoyo

---

## 📁 DATA/

Documentación relacionada con los datos utilizados por el proyecto.

Incluye:

- definición del dataset
- calidad de datos
- estructura de registros
- inventario de información

---

## 📁 EVALUATION/

Define cómo será evaluada la solución.

Incluye:

- baseline
- protocolo de evaluación
- métricas
- comparación con especialistas
- productividad

---

## 📁 DECISIONS/

Registro de decisiones importantes del proyecto (Architecture Decision Records).

Ejemplos:

- evolución Tripleta → Matriz
- alcance del MVP
- decisiones técnicas
- decisiones metodológicas

---

## 📁 AI_CONTEXT/

Contexto resumido utilizado para mantener continuidad durante el desarrollo.

Incluye:

- estado actual
- próximas tareas
- backlog
- riesgos
- decisiones recientes

---

## 📁 RESOURCES/

Material del proceso actual utilizado como fuente de verdad.

Ejemplos:

- `performance.yaml`
- `parametricConfigurationValues.yaml`
- documentación funcional
- configuraciones reales
- ejemplos corporativos

> Esta carpeta representa el funcionamiento actual del proceso de pruebas de rendimiento.

---

## 📁 src/

Código fuente principal del proyecto.

Aquí se implementarán progresivamente:

- parser YAML
- parser Gatling
- normalización
- motor de cuadrantes
- recomendador
- explicador
- API

---

## 📁 scripts/

Scripts auxiliares para:

- generación de datasets
- migraciones
- utilidades
- validaciones
- pruebas

---

## 📁 MAGISTER/

Material académico utilizado durante el desarrollo.

Incluye:

- clases
- tareas
- documentos
- retroalimentación del profesor
- presentaciones
- evidencias

---

# 🔄 Flujo del proyecto

```text
Proceso actual

performance.yaml
        │
        ▼
parametricConfigurationValues.yaml
        │
        ▼
performance-lib (Java)
        │
        ▼
Gatling
        │
        ▼
Resultados
```

↓

```text
Capstone

Información del endpoint
        │
        ▼
Parser Python
        │
        ▼
Motor de matriz
        │
        ▼
Historial
        │
        ▼
Baseline
        │
        ▼
Recomendador IA
        │
        ▼
Explicación
        │
        ▼
Validación especialista
```

---

# 📅 Estado del proyecto

Actualmente el proyecto se encuentra en la etapa de:

- ✅ Definición del problema
- ✅ Arquitectura
- ✅ Formalización de la matriz
- ✅ Definición del MVP
- 🔄 Construcción de parsers
- 🔄 Consolidación del dataset
- ⏳ Implementación del recomendador
- ⏳ Evaluación
- ⏳ Validación con especialistas

---

# 🎓 Capstone

Este proyecto forma parte del Magíster en Inteligencia Artificial y será desarrollado durante 2026.

El MVP inicial se basa en la matriz vigente de nueve cuadrantes y evoluciona hacia un sistema inteligente capaz de recomendar configuraciones de pruebas de rendimiento de forma explicable y validable.

---

# 📄 Documentación principal

| Documento | Descripción |
|------------|-------------|
| `PROJECT/CapstoneDefinition.md` | Definición general |
| `PROJECT/Problem.md` | Problema |
| `PROJECT/Objectives.md` | Objetivos |
| `PROJECT/Architecture.md` | Arquitectura |
| `PROJECT/Methodology.md` | Metodología |
| `PROJECT/DecisionMatrix.md` | Matriz de decisión |
| `PROJECT/TripletDefinition.md` | Definición de Tripleta |
| `PLANNING/ROADMAP.md` | Roadmap |
| `PLANNING/PRESENTATION_2_PLAN.md` | Plan de Presentación 2 |
| `EVALUATION/Baseline.md` | Baseline |
| `DATA/DatasetDefinition.md` | Dataset |

---

# ⚠ Estado

Proyecto en desarrollo.

La documentación y la arquitectura evolucionan conforme avanza el Capstone.