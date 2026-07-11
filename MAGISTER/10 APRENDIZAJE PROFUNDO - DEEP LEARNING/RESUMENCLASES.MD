🧠 RESUMEN GENERAL – DEEP LEARNING (PARA LA PRUEBA)
🎯 Qué evalúa la prueba (idea central)

La prueba NO evalúa código, evalúa que entiendas:

Cómo funciona una red neuronal

Por qué aprende

Qué puede y qué no puede hacer

Cómo se diseña una red según el problema

1️⃣ ¿Qué es Deep Learning?

👉 Deep Learning = modelos de aprendizaje automático basados en redes neuronales con múltiples capas

Inspiradas en el cerebro humano

Aprenden ajustando pesos, no con reglas explícitas

Funcionan bien para:

Clasificación

Regresión

Reconocimiento de patrones

Series temporales

📌 Frase típica de prueba:

El aprendizaje en redes neuronales consiste en ajustar los pesos sinápticos para minimizar una función de pérdida.

2️⃣ La neurona artificial (base de todo)
🔹 Componentes

Inputs: variables de entrada (features)

Pesos (W): importancia de cada input

Bias (b): desplaza el umbral de decisión

Suma ponderada:

𝑧
=
∑
𝑥
𝑖
𝑤
𝑖
+
𝑏
z=∑x
i
	​

w
i
	​

+b

Función de activación

Output

📌 Concepto CLAVE:

La neurona no aprende datos, aprende pesos.

3️⃣ Funciones de activación (MUY preguntable)
🔹 Escalón (Step)

Salida: 0 o 1

❌ No derivable → no sirve para backpropagation

🔹 Sigmoid

Salida entre 0 y 1

Interpretable como probabilidad

Usada en clasificación binaria

❌ Puede saturarse (gradientes pequeños)

🔹 ReLU

0 si x ≤ 0, lineal si x > 0

Usada en capas ocultas

❌ No se usa en la salida para clasificación

🔹 Softmax

Generaliza sigmoid

Convierte salidas en probabilidades que suman 1

Usada en clasificación multiclase

📌 Pregunta típica:
👉 ¿Por qué no usar ReLU en la capa de salida de clasificación?
✔️ Porque no entrega probabilidades ni valores binarios interpretables.

4️⃣ El Perceptrón
🔹 Qué es

Una sola neurona

Clasificador lineal

🔹 Qué puede hacer

✔️ Resolver problemas linealmente separables

🔹 Qué NO puede hacer

❌ Resolver problemas no lineales
❌ Resolver XOR

📌 Frase clave:

El perceptrón solo puede encontrar fronteras de decisión lineales (líneas, planos, hiperplanos).

5️⃣ Boundary decision (frontera de decisión)

Es la frontera que separa clases

Con 2 variables → línea

Con 3 variables → plano

Con n variables → hiperplano

📌 Importante:

Una neurona = una frontera lineal

Más neuronas = fronteras más complejas

Más capas = interacciones no lineales

6️⃣ Capas ocultas (hidden layers)
🔹 ¿Por qué son importantes?

Permiten modelar:

Interacciones

Cuadráticos

No linealidades

📌 Idea central:

Agregar neuronas → complejiza la frontera
Agregar capas → descubre relaciones más profundas

⚠️ Pero:

Muchas neuronas + pocos datos = overfitting

7️⃣ Aprendizaje: ¿cómo aprende la red?
🔹 Paso a paso

Pesos iniciales aleatorios

Forward pass → predicción

Comparar con valor real (target)

Calcular error (loss)

Ajustar pesos

Repetir

📌 Aprender = minimizar una función de pérdida

8️⃣ Función de pérdida (LOSS)
🔹 Regresión

MSE / RMSE

🔹 Clasificación binaria

Binary Cross Entropy (muy importante)

📌 Pregunta típica:
👉 ¿Por qué no usar MSE en clasificación?
✔️ Porque no penaliza correctamente errores probabilísticos.

9️⃣ Backpropagation (conceptual)

Método para:

Calcular gradientes

Ajustar pesos

Usa derivadas

Necesita funciones de activación derivables

📌 Clave:

Sin derivadas → no hay aprendizaje.

🔟 Learning rate (tasa de aprendizaje)

Controla qué tan grande es el ajuste

Muy grande → oscilaciones

Muy pequeño → aprendizaje lento

📌 Es un hiperparámetro

1️⃣1️⃣ Epochs y Batch size
🔹 Epoch

Una pasada completa por el dataset

🔹 Batch size

Número de muestras por actualización

Batch grande → aprendizaje más estable

Batch pequeño → más ruido

1️⃣2️⃣ Overfitting (MUY preguntable)
🔹 Qué es

Modelo aprende el entrenamiento

Falla en datos nuevos

🔹 Causas

Modelo muy complejo

Pocos datos

Muchas épocas

🔹 Cómo detectarlo

Training loss ↓

Validation loss ↑

1️⃣3️⃣ Mínimos locales vs globales

La red no garantiza encontrar el mínimo global

Gradient descent puede quedar atrapado

📌 Idea clave:

La red siempre encuentra un mínimo, no necesariamente el mejor.

1️⃣4️⃣ Métricas vs función de pérdida

⚠️ Confusión clásica de prueba

Función de pérdida	Métrica
Optimiza el aprendizaje	Evalúa desempeño
Usada para ajustar pesos	Usada para reportar resultados

Ejemplo:

Loss: Binary Cross Entropy

Métrica: Accuracy, Recall

1️⃣5️⃣ Interpretabilidad (conceptual)

Redes neuronales = caja negra

Difícil explicar causas

Riesgo en:

Salud

Banca

Psicología

📌 Pregunta conceptual típica:

¿Usarías una red neuronal para diagnosticar sin supervisión humana?

🧠 RESUMEN EXPRESS (para memorizar)

Perceptrón = lineal

XOR ≠ perceptrón

Capas ocultas → no linealidad

ReLU → capas ocultas

Sigmoid / Softmax → salida

Clasificación binaria → Binary Cross Entropy

Aprender = minimizar loss

Overfitting = memorizar

Learning rate controla velocidad

Backpropagation necesita derivadas