```markdown
# Migración de `performance-lib` y relación con el Capstone

## Situación actual

Existe una biblioteca Java denominada `performance-lib` que participa en el proceso de pruebas de rendimiento.

Entre sus funciones conocidas se encuentran:

- lectura de `performance.yaml`;
- lectura de valores parametrizados;
- resolución de configuraciones;
- preparación o ejecución de pruebas Gatling.

El detalle completo de sus responsabilidades debe confirmarse mediante revisión del código fuente.

## Propuesta

Migrar parcialmente a Python las capacidades necesarias para:

- leer configuraciones;
- validar esquemas;
- resolver cuadrantes;
- procesar resultados;
- consolidar historial;
- integrar reglas y modelos de Inteligencia Artificial.

## Rol dentro del Capstone

La migración es un habilitador técnico.

No debe presentarse como el aporte principal porque una reescritura de Java a Python corresponde principalmente a una actividad de ingeniería de software.

El aporte de IA aparece cuando la solución:

- recomienda un cuadrante;
- aprende o reutiliza patrones históricos;
- explica la recomendación;
- mide su calidad;
- incorpora feedback humano.

## Componentes recomendados para migrar

1. modelo de configuración;
2. parser de `performance.yaml`;
3. parser de valores maestros;
4. validaciones;
5. motor de resolución de matriz;
6. normalización de datos;
7. parser Gatling;
8. interfaz con el recomendador.

## Equivalencia con Java

La implementación Python debe compararse con Java utilizando los mismos archivos.

Criterios:

- mismo endpoint identificado;
- misma Tripleta;
- mismo cuadrante cuando corresponda;
- mismos valores numéricos;
- mismas validaciones;
- mismos errores ante datos inválidos;
- diferencias documentadas.

## Capacidades nuevas de Python

La versión Python podrá agregar, sin modificar inicialmente el comportamiento vigente:

- modelo de datos tipado;
- historial normalizado;
- análisis con pandas;
- reglas configurables;
- entrenamiento con scikit-learn;
- explicabilidad;
- API;
- pruebas automatizadas;
- integración con IA generativa.

## Fuera de alcance

- reemplazo productivo total;
- migración universal;
- compatibilidad con todos los repositorios;
- eliminación inmediata de Java;
- cambios automáticos sin pruebas de regresión.

## Criterio de éxito

La migración parcial será exitosa si habilita el flujo experimental del Capstone y mantiene equivalencia verificable con las funciones seleccionadas de la biblioteca Java.