# Alcance

## Incluido en el MVP

### Configuración

- lectura de `performance.yaml`;
- lectura de `parametricConfigurationValues.yaml`;
- validación de campos;
- resolución de niveles semánticos;
- identificación de la Tripleta;
- representación de criticidad;
- representación de complejidad;
- determinación de uno de nueve cuadrantes;
- resolución de parámetros asociados.

### Resultados

- lectura de resultados Gatling;
- extracción de solicitudes;
- extracción de errores;
- extracción de percentiles;
- extracción de throughput;
- extracción de assertions;
- normalización por endpoint;
- almacenamiento histórico.

### Inteligencia

- baseline basado en reglas expertas;
- recomendación inicial de cuadrante;
- recomendación de mantener, aumentar, disminuir o revisar;
- explicación de la recomendación;
- evidencia utilizada;
- validación humana;
- registro de feedback.

### Ingeniería

- implementación Python de los componentes mínimos necesarios;
- pruebas de equivalencia con la implementación Java;
- esquema de datos versionado;
- ejecución reproducible;
- trazabilidad de configuraciones y resultados.

## Alcance opcional sujeto a tiempo y datos

- clasificación automática de criticidad;
- clasificación automática de complejidad;
- modelo supervisado de cuadrantes;
- clustering de endpoints;
- análisis de Swagger;
- extracción de características mediante PLN;
- interfaz web;
- generación asistida de `performance.yaml`;
- integración automática con Gatling;
- recomendación de iteraciones.

## Fuera de alcance inicial

- reemplazo productivo completo de `performance-lib`;
- migración de todas sus capacidades;
- compatibilidad universal con todos los proyectos;
- ejecución autónoma en producción;
- cambios automáticos de infraestructura;
- despliegue corporativo completo;
- eliminación de la revisión humana;
- modificación automática de valores maestros;
- aprendizaje continuo sin supervisión;
- incorporación de variables sin datos verificables.

## Delimitación académica

El MVP debe demostrar al menos:

1. lectura de configuraciones reales;
2. procesamiento de resultados reales;
3. baseline reproducible;
4. recomendación de cuadrante;
5. explicación;
6. validación experta;
7. evaluación cuantitativa.

La migración de Java a Python no debe considerarse, por sí sola, como la contribución principal.