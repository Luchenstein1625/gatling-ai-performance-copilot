# Gate 0 · Definiciones para la defensa final

## Responsables

- **R1 · Luis Araya:** datos y modelos.
- **R2 · Hernán Medina:** recomendación.
- **R3 · Rodrigo González:** economía y documento.

## Unidad de análisis

El sistema clasifica **registros individuales**. `Build_Id` identifica los registros de una
misma ejecución y se utiliza para las particiones y los intervalos por clusters. No es la unidad
predicha.

## Semántica de la etiqueta

La etiqueta histórica `not_applies` mezcla situaciones operativamente diferentes:

1. prueba no ejecutada (`Performance = 0`);
2. ejecución con error o estado fallido;
3. evidencia incompleta;
4. combinación de las anteriores.

Por lo tanto, `not_applies` por sí sola **no indica** si corresponde aumentar o disminuir carga.
El primer paso del plan es medir la composición mediante `audit_label_causes.py` sin modificar
retroactivamente los resultados publicados.

## Política de recomendación

- Evidencia incompleta o prueba no ejecutada: **abstención** y solicitud de evidencia.
- Error de ejecución: **revisión especializada**; no cambiar carga automáticamente.
- Evidencia completa: se pueden evaluar escenarios vecinos permitidos por el YAML.
- Cada escenario modifica como máximo un parámetro y un nivel.
- La recomendación es predictiva y auditable, no causal.

## Objetivo general

Desarrollar y evaluar un sistema de apoyo a la decisión basado en aprendizaje supervisado que
permita identificar configuraciones de pruebas Gatling que requieren atención, recomendar
ajustes controlados cuando exista evidencia técnica suficiente y estimar el impacto económico
de su utilización en Banco BCI.

## Objetivos específicos

1. **OE1 · Modelamiento:** construir y comparar modelos que estimen, a nivel de registro, la
   necesidad de revisión, informando separadamente fallas y evidencia incompleta.
2. **OE2 · Recomendación:** diseñar una búsqueda restringida de configuraciones alternativas
   solo para registros con evidencia completa, con soporte histórico y posibilidad de abstención.
3. **OE3 · Economía y riesgo:** evaluar el costo, el riesgo y el beneficio potencial de las
   políticas propuestas respecto del proceso actual.

La ejecución de una nueva prueba Gatling se declara como trabajo futuro y no como objetivo del
CAPSTONE.

## Criterio de salida del Gate 0

- Causas de `not_applies` cuantificadas por filas y builds.
- Variables posteriores separadas de las entradas del modelo.
- Política de abstención documentada.
- Objetivos revisados por el equipo y el profesor guía.
- Baseline operativo pendiente de entrevista con dos analistas QA.

