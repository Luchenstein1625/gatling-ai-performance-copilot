# Definición del Capstone

## Nombre
**Gatling AI Performance Copilot**

## Definición
Sistema inteligente de apoyo a la toma de decisiones para recomendar el cuadrante de prueba de rendimiento más adecuado para cada endpoint.

Usará:
- criticidad y complejidad;
- matriz de nueve cuadrantes;
- `performance.yaml`;
- `parametricConfigurationValues.yaml`;
- resultados históricos Gatling;
- conocimiento y validación experta.

## Problema
La ejecución está parametrizada, pero la elección del cuadrante depende principalmente del criterio humano y el historial no se reutiliza sistemáticamente.

## Propuesta
1. Leer y validar configuraciones.
2. Resolver parámetros.
3. Determinar o recibir criticidad y complejidad.
4. Identificar cuadrante.
5. Procesar resultados Gatling.
6. Consolidar historial.
7. Aplicar baseline.
8. Recomendar mantener, subir, bajar o revisar.
9. Explicar la recomendación.
10. Registrar feedback humano.

## Aporte
Formalizar y reutilizar conocimiento experto mediante datos, reglas, recomendación explicable y human-in-the-loop.

## Resultado esperado
MVP reproducible, explicable y evaluado contra proceso manual y baseline.
