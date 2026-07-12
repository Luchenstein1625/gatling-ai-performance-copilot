# Experimentos

## EXP-001 — Equivalencia entre Java y Python

### Objetivo

Comprobar que la implementación Python reproduce correctamente las funciones seleccionadas de `performance-lib`.

### Entrada

- mismos archivos `performance.yaml`;
- mismos valores maestros;
- mismos endpoints.

### Métricas

- porcentaje de coincidencia;
- diferencias de parámetros;
- errores detectados;
- tiempo de procesamiento.

---

## EXP-002 — Reconstrucción del historial

### Objetivo

Procesar configuraciones y resultados históricos y generar un dataset normalizado.

### Evaluación

- ejecuciones procesadas;
- endpoints procesados;
- campos completos;
- campos desconocidos;
- errores de vinculación;
- calidad de datos.

---

## EXP-003 — Baseline de matriz

### Objetivo

Asignar cuadrantes utilizando únicamente criticidad, complejidad y la tabla vigente.

### Propósito

Establecer un punto de comparación mínimo para modelos posteriores.

### Salida

- cuadrante;
- configuración;
- explicación basada en reglas.

---

## EXP-004 — Recomendación basada en historial

### Objetivo

Evaluar si los resultados históricos permiten recomendar mantener, subir o bajar el cuadrante.

### Entradas candidatas

- cuadrante actual;
- errores;
- p95;
- p99;
- throughput;
- Apdex;
- cumplimiento de assertions;
- estabilidad histórica.

### Evaluación

- coincidencia con especialista;
- aceptación humana;
- precisión;
- F1 macro;
- errores por cuadrante.

---

## EXP-005 — Matriz ampliada

### Objetivo

Comparar la Tripleta con una matriz que incorpore variables adicionales.

### Comparaciones

1. Tripleta;
2. matriz vigente;
3. matriz ampliada;
4. criterio experto.

### Pregunta

¿Las variables adicionales mejoran la recomendación frente a la Tripleta y la matriz base?

---

## EXP-006 — Productividad

### Objetivo

Comparar el proceso manual con el proceso asistido.

### Métricas

- tiempo de selección;
- tiempo de configuración;
- correcciones;
- tiempo de análisis;
- satisfacción;
- trazabilidad.

## Reglas experimentales

- separar entrenamiento y prueba;
- evitar fuga entre ejecuciones del mismo microservicio;
- considerar orden temporal;
- registrar versiones y ambientes;
- comparar siempre con un baseline;
- documentar datos ausentes;
- no completar valores desconocidos mediante suposiciones.