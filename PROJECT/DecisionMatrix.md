# Matriz de Decisión de Pruebas de Rendimiento

## Definición

La matriz de decisión permite clasificar cada endpoint o servicio según dos dimensiones:

1. criticidad;
2. complejidad.

Cada dimensión utiliza tres niveles:

- baja;
- media;
- alta.

Su combinación genera nueve cuadrantes.

| Criticidad / Complejidad | Baja | Media | Alta |
|---|---:|---:|---:|
| Alta criticidad | Cuadrante 3 | Cuadrante 6 | Cuadrante 9 |
| Media criticidad | Cuadrante 2 | Cuadrante 5 | Cuadrante 8 |
| Baja criticidad | Cuadrante 1 | Cuadrante 4 | Cuadrante 7 |

## Interpretación general

La numeración aumenta de acuerdo con la combinación de criticidad y complejidad.

- Los cuadrantes inferiores representan configuraciones menos exigentes.
- Los cuadrantes superiores representan escenarios con mayor criticidad, complejidad o ambas.
- La selección del cuadrante define una configuración inicial de prueba.
- El historial puede recomendar mantener o modificar esa clasificación.

---

## Cuadrante 1

### Clasificación

- criticidad: baja;
- complejidad: baja.

### Parámetros

- concurrencia: 5 VU;
- iteraciones: N, dependiente de otros factores;
- tiempo de respuesta esperado: 1 segundo;
- Apdex esperado: mayor o igual a 0,95;
- interpretación Apdex: excelente;
- throughput esperado: alto, mayor o igual a 10 TPS;
- ramp-up: entre 1 y 2 minutos;
- duración: entre 2 y 4 minutos;
- cantidad VU: 40.

---

## Cuadrante 2

### Clasificación

- criticidad: media;
- complejidad: baja.

### Parámetros

- concurrencia: 10 VU;
- iteraciones: N, dependiente de otros factores;
- tiempo de respuesta esperado: 2 segundos;
- Apdex esperado: mayor o igual a 0,90;
- interpretación Apdex: muy bueno;
- throughput esperado: alto, mayor o igual a 10 TPS;
- ramp-up: entre 2 y 3 minutos;
- duración: entre 4 y 6 minutos;
- cantidad VU: 50.

---

## Cuadrante 3

### Clasificación

- criticidad: alta;
- complejidad: baja.

### Parámetros

- concurrencia: 15 VU;
- iteraciones: N, dependiente de otros factores;
- tiempo de respuesta esperado: 4 segundos;
- Apdex esperado: mayor o igual a 0,75;
- interpretación Apdex: bueno;
- throughput esperado: alto, mayor o igual a 10 TPS;
- ramp-up: entre 3 y 4 minutos;
- duración: entre 5 y 7 minutos;
- cantidad VU: 60.

---

## Cuadrante 4

### Clasificación

- criticidad: baja;
- complejidad: media.

### Parámetros

- concurrencia: 20 VU;
- iteraciones: N, dependiente de otros factores;
- tiempo de respuesta esperado: 5 segundos;
- Apdex esperado: mayor o igual a 0,70;
- interpretación Apdex: aceptable;
- throughput esperado: medio, 8 TPS;
- ramp-up: entre 4 y 5 minutos;
- duración: entre 6 y 8 minutos;
- cantidad VU: 70.

---

## Cuadrante 5

### Clasificación

- criticidad: media;
- complejidad: media.

### Parámetros

- concurrencia: 25 VU;
- iteraciones: N, dependiente de otros factores;
- tiempo de respuesta esperado: 6 segundos;
- Apdex esperado: mayor o igual a 0,75;
- interpretación Apdex: aceptable;
- throughput esperado: medio, 8 TPS;
- ramp-up: entre 5 y 6 minutos;
- duración: entre 8 y 10 minutos;
- cantidad VU: 80.

---

## Cuadrante 6

### Clasificación

- criticidad: alta;
- complejidad: media.

### Parámetros

- concurrencia: 30 VU;
- iteraciones: N, dependiente de otros factores;
- tiempo de respuesta esperado: 7 segundos;
- Apdex esperado: mayor o igual a 0,75;
- interpretación Apdex: aceptable;
- throughput esperado: medio, 8 TPS;
- ramp-up: entre 6 y 7 minutos;
- duración: entre 10 y 15 minutos;
- cantidad VU: 80.

---

## Cuadrante 7

### Clasificación

- criticidad: baja;
- complejidad: alta.

### Parámetros

- concurrencia: 35 VU;
- iteraciones: N, dependiente de otros factores;
- tiempo de respuesta esperado: 8 segundos;
- Apdex esperado: mayor o igual a 0,60;
- interpretación Apdex: bajo;
- throughput esperado: bajo, 4 TPS;
- ramp-up: entre 7 y 8 minutos;
- duración: entre 10 y 15 minutos;
- cantidad VU: 100.

---

## Cuadrante 8

### Clasificación

- criticidad: media;
- complejidad: alta.

### Parámetros

- concurrencia: 40 VU;
- iteraciones: N, dependiente de otros factores;
- tiempo de respuesta esperado: 10 segundos;
- Apdex esperado: mayor o igual a 0,55;
- interpretación Apdex: muy bajo;
- throughput esperado: bajo, 4 TPS;
- ramp-up: entre 8 y 10 minutos;
- duración: entre 15 y 20 minutos;
- cantidad VU: 120.

---

## Cuadrante 9

### Clasificación

- criticidad: alta;
- complejidad: alta.

### Parámetros

- concurrencia: 45 VU;
- iteraciones: N, dependiente de otros factores;
- tiempo de respuesta esperado: 12 segundos;
- Apdex esperado: mayor o igual a 0,50;
- interpretación registrada en la matriz: inaceptable;
- throughput esperado: bajo, 4 TPS;
- ramp-up: entre 10 y 12 minutos;
- duración: entre 20 y 25 minutos;
- cantidad VU: 140.

## Ejemplos entregados por el proceso actual

### Alta criticidad

Servicios de cara a clientes, por ejemplo:

- login;
- consultas de saldo;
- transferencias electrónicas;
- pago de cuentas.

### Alta complejidad

Servicios que poseen dependencias o se conectan con diferentes fuentes de datos, por ejemplo:

- base de datos relacional;
- Tándem;
- IBM;
- otras plataformas.

## Aspectos pendientes de validación

### Concurrencia versus cantidad VU

La matriz contiene dos valores distintos:

- concurrencia;
- cantidad VU.

Debe confirmarse formalmente qué representa cada uno.

No se debe asumir que ambos conceptos son equivalentes.

Hipótesis pendiente de validación:

- concurrencia podría representar usuarios simultáneos por endpoint;
- cantidad VU podría representar el total de usuarios virtuales de la prueba.

Esta interpretación no debe implementarse hasta ser confirmada por QA Infraestructura.

### Iteraciones

Las iteraciones aparecen declaradas como `N` y dependen de otros factores.

Debe definirse:

- cuáles son esos factores;
- cómo se calcula N;
- si depende de duración;
- si depende de cantidad VU;
- si depende de throughput;
- si se configura manualmente;
- si puede ser recomendado por el sistema.

### Apdex

Debe confirmarse:

- fórmula utilizada;
- umbral de satisfacción;
- umbral de tolerancia;
- fuente de cada valor;
- sentido de utilizar un Apdex esperado menor en cuadrantes de mayor complejidad.

### Throughput

Debe confirmarse si los valores indicados corresponden a:

- objetivo mínimo;
- promedio esperado;
- límite;
- clasificación cualitativa;
- TPS globales;
- TPS por endpoint.

## Evolución futura

La matriz podrá incorporar variables adicionales como:

- método HTTP;
- tipo de operación;
- criticidad regulatoria;
- criticidad de negocio;
- dependencia externa;
- reason tag;
- volumen productivo;
- percentiles históricos;
- porcentaje de errores;
- estabilidad entre ejecuciones;
- ambiente;
- versión;
- recursos de infraestructura;
- feedback del especialista.

Las variables nuevas deben incorporarse únicamente cuando exista una definición verificable y datos suficientes.