# Support Vector Machine

## Definición
Modelo que busca un hiperplano de separación con el mayor margen posible.

## Aplicación al Capstone
Clasificar cuadrantes en datasets pequeños o medianos.

## Ventajas
Buen desempeño en espacios de alta dimensión.

## Limitaciones
Menor explicabilidad y ajuste sensible de kernel e hiperparámetros.

## Datos requeridos
- variables de entrada claramente definidas;
- datos comparables;
- tratamiento de valores faltantes;
- partición de entrenamiento y validación;
- prevención de fuga de información.

## Evaluación
El algoritmo debe compararse con el baseline y evaluarse con métricas apropiadas por clase, especialmente cuando los cuadrantes estén desbalanceados.

## Explicabilidad
Debe documentarse cómo se interpreta la salida y qué evidencia se entrega al especialista.

## Estado
Candidato. La selección definitiva depende del dataset, baseline y validación con expertos.

## Relación con el Magíster
Principalmente Aprendizaje Automático y Tópicos Avanzados en IA I.

## Próximos pasos
- probar con datos reales;
- registrar hiperparámetros;
- comparar resultados;
- documentar decisión en `DECISIONS/`.
