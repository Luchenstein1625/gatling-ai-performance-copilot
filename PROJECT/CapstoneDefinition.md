# Definición del Capstone

## Nombre

**Gatling AI Performance Copilot**

## Definición

Gatling AI Performance Copilot es un sistema inteligente de apoyo a la toma de decisiones para la configuración de pruebas de rendimiento.

Su propósito es asistir a los especialistas y equipos responsables de las pruebas en la selección del cuadrante más adecuado para cada endpoint, considerando su nivel de criticidad, complejidad, configuración técnica, resultados históricos y conocimiento experto.

El proceso actual utiliza una matriz de decisión formada por nueve cuadrantes. Cada cuadrante surge de la combinación de dos dimensiones:

- criticidad del endpoint o servicio;
- complejidad del endpoint o servicio.

Cada dimensión posee tres niveles:

- baja;
- media;
- alta.

La combinación de estos niveles determina uno de nueve cuadrantes, desde el Cuadrante 1 hasta el Cuadrante 9.

## Relación con la Tripleta

La Tripleta actualmente utilizada está formada por:

- concurrencia;
- iteraciones;
- tiempo de respuesta esperado.

La Tripleta continúa siendo parte importante de la configuración, pero no representa por sí sola toda la matriz de decisión.

La matriz ampliada incorpora otros parámetros como:

- Apdex esperado;
- throughput esperado;
- ramp-up;
- duración;
- cantidad de usuarios virtuales;
- criticidad;
- complejidad.

Por lo tanto, el proyecto evoluciona desde la recomendación de una Tripleta hacia la recomendación de un cuadrante completo.

## Problema

Actualmente la clasificación de criticidad y complejidad, así como la selección del cuadrante, depende principalmente del conocimiento y criterio de los especialistas.

Aunque existen reglas y valores predefinidos, el historial de ejecuciones Gatling no se reutiliza de forma sistemática para:

- validar si el cuadrante fue apropiado;
- recomendar ajustes;
- identificar configuraciones sobredimensionadas;
- identificar configuraciones subdimensionadas;
- estandarizar decisiones entre equipos;
- explicar por qué se seleccionó un determinado cuadrante.

## Propuesta

El Capstone propone desarrollar un copiloto inteligente capaz de:

1. leer la información funcional y técnica de un endpoint;
2. determinar o recibir su criticidad;
3. determinar o recibir su complejidad;
4. identificar el cuadrante inicial correspondiente;
5. resolver los parámetros asociados al cuadrante;
6. leer la configuración declarada en `performance.yaml`;
7. utilizar los valores maestros de `parametricConfigurationValues.yaml`;
8. analizar resultados históricos y actuales de Gatling;
9. recomendar mantener, aumentar, disminuir o revisar el cuadrante;
10. explicar la recomendación;
11. permitir la validación del especialista;
12. registrar el feedback humano para futuras recomendaciones.

## Aporte principal

El aporte principal del proyecto no consiste únicamente en ejecutar Gatling ni en migrar una biblioteca desde Java a Python.

El valor del Capstone consiste en formalizar y reutilizar el conocimiento experto utilizado para seleccionar configuraciones de rendimiento, complementándolo con información histórica y mecanismos de Inteligencia Artificial explicables.

## Usuario objetivo

- especialistas de QA Infraestructura;
- ingenieros de rendimiento;
- equipos que configuran pruebas mediante `performance.yaml`;
- responsables de revisar y aprobar escenarios de carga.

## Resultado esperado

Un MVP que reciba información de un endpoint, identifique o recomiende un cuadrante, reconstruya su configuración, analice sus resultados Gatling y entregue una recomendación explicable, validable y trazable.