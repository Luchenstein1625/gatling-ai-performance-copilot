# Q Learning

## Definición
Algoritmo de aprendizaje por refuerzo que estima el valor de acciones en estados.

## Aplicación al Capstone
Trabajo futuro para ajustar progresivamente estrategias de prueba.

## Ventajas
Aprende políticas sin modelo explícito del entorno.

## Limitaciones
Requiere función de recompensa, exploración segura y muchas interacciones.

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
