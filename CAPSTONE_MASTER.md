# CAPSTONE MASTER

> Proyecto: Gatling AI Performance Copilot  
> Versión: 1.0.0  
> Estado: En definición y validación  
> Última actualización: 2026-07-11

## Información general
- Universidad: Universidad Adolfo Ibáñez
- Programa: Magíster en Inteligencia Artificial
- Integrantes: Luis Araya, Rodrigo González y Hernán Medina
- Profesor guía: Ahmad Armoush

## Historia
La propuesta inicial fue un sistema de Capacity Planning Cloud. La P1 obtuvo nota 4,0 y el equipo detectó problemas de alcance, acceso a datos, concreción, métricas y demostrabilidad.

## Propuesta activa
Sistema inteligente que:
1. recibe metadatos y requisitos de un microservicio;
2. genera un script Gatling mediante IA generativa;
3. ejecuta una prueba inicial en un cuadrante medio;
4. procesa métricas históricas y actuales;
5. recomienda el cuadrante futuro;
6. explica la recomendación;
7. mantiene validación humana.

## Problema preliminar
La preparación de pruebas de rendimiento depende de trabajo manual y criterios variables. El historial de cada microservicio no se utiliza de forma sistemática para definir cargas, lo que genera baja estandarización, reprocesos y escenarios potencialmente subdimensionados o sobredimensionados.

## Hipótesis preliminar
La combinación de IA generativa y aprendizaje sobre resultados históricos reducirá el tiempo de preparación, mejorará la consistencia y permitirá recomendar cargas más representativas que el proceso manual.

## Objetivo general preliminar
Diseñar y validar un sistema inteligente que automatice la generación de pruebas de rendimiento con Gatling y recomiende dinámicamente el cuadrante de prueba de cada microservicio a partir de su historial de ejecuciones.

## Objetivos específicos
1. Caracterizar el proceso actual.
2. Automatizar la generación inicial de scripts.
3. Definir cuadrantes cuantitativos.
4. Consolidar un historial comparable.
5. Implementar un mecanismo de recomendación.
6. Evaluar el sistema contra el proceso manual.
7. Medir productividad, calidad técnica y utilidad.

## Métricas candidatas
- p90 y p95
- throughput y TPS
- porcentaje de errores
- tiempo de generación
- tasa de compilación
- correcciones manuales
- coincidencia con criterio experto
- precisión, recall y F1 cuando existan etiquetas
- tasa de aceptación humana

## Cuadrantes preliminares
- Bajo
- Medio
- Alto
- Crítico

Los umbrales concretos deben validarse con datos y expertos.

## Arquitectura conceptual
- ingesta;
- generador LLM;
- validador técnico;
- orquestador;
- parser Gatling;
- persistencia histórica;
- motor de reglas o aprendizaje;
- explicador;
- human in the loop.

## Riesgos
- historial insuficiente;
- cuadrantes subjetivos;
- scripts inválidos;
- alcance excesivo;
- confidencialidad;
- variabilidad entre ambientes;
- falta de etiquetas;
- baja explicabilidad.

## Asignaturas relacionadas
Aprendizaje Automático, Agentes Inteligentes, PLN, Representación del Conocimiento, Tópicos Emergentes, Tópicos Avanzados, Simulación Basada en Agentes, Taller de Diseño e Innovación, Deep Learning y Capstone.

## Decisiones vigentes
- DEC-001: descartar Capacity Planning.
- DEC-002: adoptar Gatling AI Performance Copilot.
- DEC-003: usar cuadrante medio inicial de forma provisional.
- DEC-004: usar GitHub y Markdown como fuente única de verdad.

## Próximas definiciones
Datos, microservicios, cuadrantes, baseline, modelo, arquitectura mínima, KPIs, protocolo de evaluación y alcance de P2.
