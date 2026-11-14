# Plan de mejora · Capstone P3 · Performance Intelligence Copilot

**Ventana:** lunes 16-nov-2026 → viernes 8-ene-2027 (8 semanas; feriados: mar 8-dic, vie 25-dic, vie 1-ene).
**Base del plan:** feedback del profesor en la grabación `UAI_P3_Grupo8` + estado de la presentación v32 (22 láminas).
**Equipo:** Hernán Medina · Luis Araya · Rodrigo González (asignar R1, R2, R3 en la semana 1).
**Supuesto a confirmar:** la fecha de defensa/entrega final no aparece en la grabación. El plan congela entregables el **mié 6-ene** y deja el 7–8 de enero de colchón; si la fecha es anterior, se comprime desde la semana 7.

---

## 0. Qué cambia en una frase

El profesor dijo que **solo el objetivo 1 (clasificar) está bien desarrollado**; que *priorizar* es un subproducto, *validar* es post-capstone, y que **recomendar** no tiene método ni resultado explícito. El plan convierte el capstone en un trabajo con **tres objetivos comparables y completamente respondibles**:

1. **OE1 · Modelamiento predictivo** (clasificar, con priorización como salida).
2. **OE2 · Recomendación** (el hueco principal): optimización discreta sobre el modelo, evaluada offline.
3. **OE3 · Evaluación económica y de riesgo** (hoy está hecha pero no es un objetivo).

La validación en Gatling pasa a **trabajo futuro**.

---

## 1. Trazabilidad del feedback (qué dijo → qué hacemos)

Estado frente a v32: ✅ cubierto · 🟡 parcial · ❌ no cubierto.

| ID | Feedback del profesor | Acción | Entregable | Sem. | Criterio de aceptación | v32 |
|---|---|---|---|---|---|---|
| F1 | Lámina 2: falta el **impacto económico** del problema (impacto unitario × frecuencia) | Calculadora de impacto con supuestos explícitos (sec. 4.3-A) | Lámina 2 con cifra + hoja de supuestos | 2–3 | Fórmula visible, rangos bajo/base/alto, fuente de cada supuesto | ❌ |
| F2 | Objetivo general con **redacción académica** | Reescribir (sec. 3) y validar con profesor guía | Texto de objetivos v1 → v2 | 1 | Verbo de acción medible, objeto, método, contexto, criterio de evaluación | ❌ |
| F3 | Objetivos específicos = **grandes dimensiones comparables**. "Priorizar" no lo es | OE1/OE2/OE3 (sec. 3); priorizar pasa a métrica de OE1 | Lámina 3 rediseñada | 1 | Tres OE del mismo nivel, cada uno con método, resultado y métrica | ❌ |
| F4 | **Validar** es post-capstone: sacarlo de objetivos y la lámina 14 | Mover a trabajo futuro; si se menciona, solo en la defensa | Deck sin lámina de validación en el cuerpo | 8 | Ninguna lámina del cuerpo promete validación online | ❌ |
| F5 | Incorporar **evaluación económica** como objetivo (matriz 10/2/1, penalizaciones) | OE3 + Monte Carlo + curva de decisión (sec. 4.3) | Sección de resultados OE3 | 5–7 | Sensibilidad, break-even y probabilidad de ROI > 0 | 🟡 |
| F6 | **Recomendación**: sin método, sin resultado; ¿cómo sabe el modelo qué parámetro subir o bajar? Esperaba **optimización** | OE2 completo (sec. 4.2) | Motor de recomendación + tabla de resultados | 3–6 | Respuesta técnica en 3 frases + evaluación offline con IC | ❌ |
| F7 | **Unidad de análisis**: ¿registro o build? (se clasifica registro; Build_Id solo para particiones) | Definir y repetir en todo el deck; pruebas automáticas de no-fuga | Lámina "Unidad de análisis" | 1–2 | Un solo nivel de clasificación declarado; 0 Build_Id cruzados | 🟡 |
| F8 | Lámina 6: explicar el gráfico P95 y la **distribución aplica/no aplica en cantidades** | Tablas y gráficos con conteos (registros y builds) | Lámina de EDA rehecha | 2 | Cada gráfico dice qué mide, en qué unidad y con qué n | ❌ |
| F9 | Partición **train/dev/test** (dev ≈ 10 % para hiperparámetros) | Protocolo 70/10/20 por Build_Id, test bloqueado | Lámina del protocolo | 2 | Test usado una sola vez, con registro del hash de los Build_Id | 🟡 |
| F10 | **Baseline** poco claro: debe ser lo que hace la compañía hoy | Cuatro baselines B0–B3 (sec. 4.1-D); B2 codifica el criterio del analista | Lámina de baselines | 2–3 | Cada baseline con definición operativa y fuente | ❌ |
| F11 | Incorporar **boosting** (o reemplazar RF); historia de ensambles progresivos; regresión: usarla o sacarla | Árbol → RF → boosting (+ stacking opcional); regresión como modelo interpretable | Tabla comparativa con IC | 4 | Decisión basada en diferencia pareada con IC, no en un punto | ❌ |
| F12 | Lámina 14: **sacarla del alcance** | Eliminar; reutilizar como anexo de defensa | — | 8 | No figura en el cuerpo | ❌ |
| F13 | Láminas finales: **máx. 2 ideas potentes** de trabajo futuro | Dos líneas (sec. 9) | Lámina final | 8 | Dos ideas con problema, enfoque y beneficio | 🟡 |
| F14 | Revisar con más detalle el OE3 original (recomendación) **y su resultado** | Ver F6 | Ver F6 | 3–6 | Ver F6 | ❌ |

*Positivo a conservar:* el profesor valoró lo visual y la mejora respecto de presentaciones previas. No se rediseña la identidad visual; se ordena el contenido.

---

## 2. Seis decisiones que se toman en la semana 1 (antes de tocar código)

| # | Decisión | Por qué importa | Propuesta |
|---|---|---|---|
| D1 | **Unidad de análisis** | F7 | Registro. Build_Id = grupo para particionar y para el bootstrap por clusters |
| D2 | **Semántica de "no aplica"**: ¿subir o bajar carga? | Sin esto la recomendación no tiene dirección | Matriz carga × resultado (sec. 4.2-A) y entrevista a 2 analistas |
| D3 | **Etiqueta con margen** | El profesor notó que hay pruebas que "pasan raspando" | Etiqueta ordinal: *falla / pasa justo / pasa con holgura* (sec. 4.2-A) |
| D4 | **Qué modelo sirve a OE1 y OE2** | Evitar dos modelos desconectados | Un solo modelo ex ante f(contexto, configuración). Se evalúa con y sin Método/CpruebasAcep por gobierno de datos |
| D5 | **Qué es el baseline** | F10 | B2 = heurística del analista codificada; B0 = azar a igual capacidad |
| D6 | **Fecha de defensa y formato de entrega** (paper, informe, ambos) | Define el colchón | Preguntar al profesor guía el miércoles 18-nov |

---

## 3. Nuevo marco académico

**Objetivo general (propuesta).** Desarrollar y evaluar, mediante aprendizaje supervisado sobre registros históricos de pruebas de carga Gatling del Banco BCI, un sistema de apoyo a la decisión que estime el riesgo de que una configuración de prueba no cumpla sus criterios, recomiende ajustes acotados de parámetros y cuantifique el valor económico y el riesgo operacional de su uso bajo supuestos explícitos.

**Objetivos específicos (propuesta).**

- **OE1.** Construir y comparar modelos de clasificación (baselines, regresión logística, bosque aleatorio y boosting) que estimen, a nivel de registro, la probabilidad de incumplimiento, bajo un protocolo de partición agrupada por Build_Id con conjuntos de entrenamiento, desarrollo y prueba, evaluando discriminación, calibración y capacidad de priorización con intervalos de confianza por clusters.
- **OE2.** Diseñar un procedimiento de recomendación de parámetros (concurrencia, iteraciones y tiempo de respuesta) basado en optimización discreta restringida sobre el modelo de OE1, y evaluar su coherencia y validez mediante pruebas de monotonía, retrospectivas históricas y estabilidad.
- **OE3.** Estimar el impacto económico y el riesgo operacional de las políticas de priorización y de liberación mediante una función de costo asimétrica, análisis de sensibilidad probabilístico y puntos de equilibrio.

**Preguntas e hipótesis (se pre-registran en el repo antes de correr el test).**

| | Pregunta | Hipótesis contrastable |
|---|---|---|
| PI1 | ¿Un boosting discrimina mejor que RF y que los baselines? | H1: ΔROC-AUC (boosting − RF) > 0 con IC95 % que excluye 0 en test |
| PI2 | ¿Las recomendaciones concuerdan con la evidencia histórica? | H2: la concordancia retrospectiva es mayor que la de recomendar al azar (IC95 % excluye el valor del azar) |
| PI3 | ¿Priorizar reduce el costo esperado frente a revisar todo? | H3: costo(política) < costo(revisar todo) en > 50 % de los escenarios Monte Carlo |

**Dónde quedan los otros temas.**

- *Priorizar* → métrica de OE1 (recall@k, precisión@k, lift, curva de ganancia).
- *Validar en Gatling* → trabajo futuro y limitaciones (sec. 9). No es objetivo.

---

## 4. Especificación técnica por objetivo

### 4.1 · OE1 · Modelamiento predictivo

**A. Unidad y etiqueta.**
- Unidad: **registro** (configuración + contexto + resultado). Build_Id solo agrupa.
- Etiqueta binaria actual: `applies` / `not_applies` (regla de la lámina 5).
- Etiqueta con margen (nueva): `headroom = 1 − p95 / objetivo_ms`. Clases: **falla** (no cumple), **pasa justo** (0 ≤ headroom < h₁) y **pasa con holgura** (headroom ≥ h₁). Se define h₁ con los analistas (candidatos 10 %, 20 %). Solo para registros completos.

**B. Variables ex ante (permitidas).** Concurrency, Iterations, ResponseTime, pilar, componente, ambiente, CpruebasCarga; Método y CpruebasAcep solo bajo gobierno de datos.
Variables derivadas (nuevas):
- `carga_total = concurrency × iterations`.
- `presion = carga_total / objetivo_ms`.
- `nivel_relativo`: nivel de carga respecto de la mediana histórica del componente.
- `tasa_historica_componente`: tasa de incumplimiento por componente **calculada fuera de la muestra de cada fold** (target encoding anidado, para no filtrar información).

**C. Protocolo de partición (F9).**

| Conjunto | % | Uso |
|---|---|---|
| Train | 70 | Ajuste de modelos |
| Dev | 10 | Hiperparámetros, calibración, elección de umbral |
| Test | 20 | Una sola evaluación final |

- Partición con `StratifiedGroupKFold` por Build_Id, semilla fija.
- Se guarda el hash de los Build_Id de test y se hace commit **antes** de entrenar (pre-registro).
- Como el número de builds es pequeño (≈ 122 en test filtrado), se agrega validación cruzada agrupada repetida (5×3) sobre train+dev como análisis de robustez, no para elegir el modelo final.

**D. Baselines (F10).**

| ID | Definición | Representa |
|---|---|---|
| B0 | Revisar en orden aleatorio con la misma capacidad (30 %) | Piso estadístico |
| B1 | Clase mayoritaria | Referencia métrica (no operativa) |
| B2 | **Heurística del analista** codificada tras entrevista (reglas por carga y componente) | Lo que hace la compañía hoy |
| B3 | Tasa histórica de incumplimiento por componente/pilar | "Memoria institucional" barata y fuerte |

**E. Modelos (historia en tres actos).** Árbol → bosque aleatorio (RF) → **boosting** (HistGradientBoosting, LightGBM, XGBoost, CatBoost). Se mantiene la regresión logística como modelo interpretable, con coeficientes y odds ratio. Opcionales: stacking (logística + boosting) y regresión logística ordinal.

- **Restricciones de monotonía** en boosting: más carga no puede reducir el riesgo de falla; objetivo de tiempo más exigente no puede reducirlo. Codifica conocimiento de dominio y hace coherentes las recomendaciones.
- Tuning con Optuna sobre dev (≥ 100 ensayos por modelo, mismos presupuestos).

**F. Métricas e incertidumbre.** ROC-AUC, PR-AUC (contra prevalencia), recall@k y precisión@k (k = 10/20/30 %), lift, Brier y ECE (calibración). Todo con **bootstrap por clusters de Build_Id** (2.000 réplicas) y **diferencias pareadas** entre modelos.

**G. Explicabilidad.** SHAP (TreeExplainer), importancia por permutación y curvas ICE/PDP. Se reporta explícitamente que miden asociación predictiva.

**H. Umbral con garantía estadística.** Cota superior exacta (Clopper–Pearson) del porcentaje de not_applies entre los liberados, calculada en dev, con corrección por múltiples umbrales (secuencia fija / Learn-then-Test). Se elige el mayor conjunto liberable cuya cota sea ≤ 5 %. **Si no existe ninguno, ese es el resultado**: "no se puede liberar con garantía", cuantificado.

### 4.2 · OE2 · Recomendación (el hueco que señaló el profesor)

**A. Semántica (lo primero).** Hoy hay ambigüedad: ¿"no aplica" pide subir o bajar la carga? Se resuelve con una matriz que los analistas validan:

| Resultado de la prueba | Interpretación | Recomendación natural |
|---|---|---|
| Pasa con holgura | Posible **subdimensionamiento** (no estresa) | Subir un nivel de carga |
| Pasa justo | Zona objetivo | Mantener |
| Falla | Posible **sobredimensionamiento** o servicio deficiente | Bajar un nivel o relajar el objetivo |

Esto responde al profesor: dirección y parámetro salen de **qué tan cerca del límite** se predice el resultado, no de un "subir" fijo.

**B. Formalización.**

- Contexto x (inmutable): pilar, componente, ambiente, método.
- Configuración a = (c, i, r), con niveles discretos de `parametricConfigurationValues.yaml` (p. ej. concurrencia 60/80; tiempo de respuesta 3.000/8.000 ms).
- Modelo calibrado de OE1: P(Y ∈ zona objetivo | x, a).
- Política: a\* = argmax sobre A(x, a₀) de **U(a) = P(zona objetivo | x, a) − λ·Costo(a)**, donde A restringe a **cambiar un solo parámetro un nivel** (atribución causal limpia, tal como se dijo en la presentación) o mantener.
- Con ≈ 27–81 configuraciones, la **búsqueda exhaustiva es exacta**: no se necesita optimización bayesiana (se justifica en una línea en el documento).
- Se recomienda solo si ΔP ≥ δ y el **límite inferior del IC (bootstrap de modelos) > 0**. Si no, **se abstiene**: "mantener / sin evidencia".
- Se exige **soporte**: mínimo k registros históricos en la celda (contexto, configuración destino). Sin soporte no hay recomendación (evita extrapolar).

**C. Resultado que genera el módulo (respuesta a "¿cuál es el resultado?").** *Tarjeta de recomendación* por caso: contexto, configuración actual, riesgo actual, parámetro a modificar, nivel destino, ΔP con IC95 %, costo relativo de carga, soporte (n), confianza (alta/media/abstención) y razón (SHAP + curva ICE).

**D. Evaluación offline (sin Gatling).**

| Prueba | Qué mide | Criterio de éxito |
|---|---|---|
| E1 Monotonía | % de contextos donde más carga no reduce el riesgo | ≥ 99 % |
| E2 Retrospectiva | En contextos con ≥ 2 configuraciones observadas: ¿la recomendada coincide con la que tuvo mejor resultado? (τ de Kendall, exactitud por pares) | IC95 % excluye el azar (H2) |
| E3 Contrafactuales | Comparar con DiCE (cambios mínimos con restricciones de factibilidad) | Coincidencia ≥ 70 % |
| E4 Estabilidad | Consistencia de la recomendación entre réplicas bootstrap | ≥ 80 % |
| E5 Baselines | "Siempre subir", "mantener", aleatoria, regla del analista | Supera a las cuatro o se reporta honestamente |
| E6 Cobertura | % de casos con recomendación accionable vs. abstención | Reportado, sin meta |

**E. Respuesta de defensa (30 segundos).** "El clasificador entrega probabilidades calibradas sobre contexto y configuración. Para cada prueba evaluamos todas las configuraciones vecinas permitidas, un parámetro a la vez, y elegimos la que maximiza la probabilidad de caer en la zona objetivo menos un costo de carga, solo si la mejora es estadísticamente distinguible y hay datos históricos que la respalden. Lo evaluamos offline con monotonía, retrospectivas y estabilidad; la validación en Gatling es trabajo futuro."

**F. Limitaciones que se declaran (amenazas a la validez).** Datos observacionales: la configuración la eligió un analista según el componente (sesgo de selección); el efecto es predictivo, no causal; se mitiga con soporte mínimo, comparaciones dentro del mismo contexto y abstención.

### 4.3 · OE3 · Evaluación económica y de riesgo

**A. Impacto del problema (F1, lámina 2).** Fórmula:

`Impacto anual = N × [ p_sub × C_riesgo + p_sobre × C_reejecución ]`

- N: pruebas o atenciones por año (hoy 144 atenciones × $224 mil = **$32,26 MM** de base presupuestaria).
- p_sub, p_sobre: frecuencia de decisiones mal calibradas (se estiman con los datos y con los analistas).
- C_reejecución: horas del analista × tarifa + costo de la ventana de prueba.
- C_riesgo: costo esperado de una falla no detectada (horas de incidente × costo/hora; se pide a Riesgo/Operaciones).

*Ejemplo ilustrativo (supuestos, no datos):* si entre 20 % y 40 % de las atenciones requirieran reejecución, el costo de repetir trabajo estaría entre **$6,5 MM y $12,9 MM al año**; cada punto porcentual de esfuerzo QA mal asignado equivale a ≈ **$0,32 MM/año**. Se presenta como rango con fuente, y el profesor pidió justamente "un estimado, no la evaluación fina".

**B. Función de costo.** Se conserva 10/2/1 y se agrega **calibración de supuestos**: un rango plausible para cada parámetro (revisión, applies revisado, falso applies) elegido con los analistas.

**C. Sensibilidad probabilística (Monte Carlo).** Distribuciones triangulares para cobertura, reducción de esfuerzo, costos y prevalencia; 10.000 simulaciones; gráfico tornado y **probabilidad de ROI > 0**. Se mantiene el *break-even* (cobertura × reducción ≥ 4,0 % con la base actual).

**D. Curva de decisión (decision curve analysis).** Beneficio neto vs. "revisar todo" y "no revisar nada" en función del umbral; responde "¿para qué valores de costo conviene el modelo?" con una sola figura.

---

## 5. Cronograma semana a semana

Capacidad supuesta: 6–8 h por persona por semana (≈ 18–24 h de equipo). Semanas 6–7 con capacidad al 50 % por feriados. R1 = datos/modelos, R2 = recomendación, R3 = economía y documento (rotan).

| Sem. | Fechas | Foco | Hito de salida |
|---|---|---|---|
| 1 | 16–20 nov | Definir y congelar | **Gate 0**: definiciones D1–D6 aprobadas |
| 2 | 23–27 nov | Datos y protocolo | Split 70/10/20 bloqueado; baselines definidos |
| 3 | 30 nov–4 dic | Modelos clásicos reproducibles | **Gate 1**: protocolo y baselines aprobados |
| 4 | 7–11 dic (8-dic feriado) | Boosting, tuning, explicabilidad | Tabla comparativa con IC |
| 5 | 14–18 dic (15-dic mañana ocupada) | Calibración, umbral con garantía, recomendador v0 | **Gate 2**: modelo congelado (tag) |
| 6 | 21–24 dic (25-dic feriado) | Recomendador completo y evaluación offline; **test una sola vez** | **Gate 3**: resultados de test |
| 7 | 28–31 dic (1-ene feriado) | Economía (Monte Carlo) y borrador del documento | Documento v0.8 |
| 8 | 4–8 ene | Integración, deck v33, ensayos, congelado el mié 6 | **Gate 4**: entregable final |

### Semana 1 · 16–20 nov · Definir y congelar (≈ 22 h)

- **Lun 16 (2 h, todos):** reunión de alineación; revisar esta tabla; asignar R1/R2/R3.
- **Lun–mar (3 h, R3):** objetivos académicos v1 (sec. 3), preguntas e hipótesis.
- **Mar–mié (4 h, R2):** matriz carga × resultado; guía de entrevista (sec. 11-B); 2 entrevistas de 45 min a analistas (baseline B2, definición de h₁, zona objetivo).
- **Lun–mié (5 h, R1):** inventario de datos con **conteos**: registros y builds por clase, por componente, por pilar, por ambiente; cuántas configuraciones distintas por contexto (soporte).
- **Mié 18 (1 h, todos):** reunión con profesor guía (preguntas en sec. 11-A).
- **Jue–vie (4 h, todos):** documento *Definiciones v1* (3 págs.): unidad, etiqueta, semántica, baseline, protocolo, alcance. Crear repo con estructura (sec. 7).
- **Vie 20: Gate 0.** Pasa si: los 3 OE están aprobados por el guía y la semántica de "no aplica" quedó escrita.

### Semana 2 · 23–27 nov · Datos y protocolo (≈ 22 h)

- **R1 (8 h):** partición 70/10/20 agrupada y estratificada; hash de Build_Id de test; pruebas automáticas (sin cruce de Build_Id, sin variables prohibidas); cálculo del headroom.
- **R2 (6 h):** B0–B3 implementados; protocolo de "soporte" para el recomendador.
- **R3 (6 h):** EDA nueva (F8): gráficos con n, unidad y qué mide el p95; tabla de distribución aplica/no aplica por registro y por build; solicitud de datos a BCI para la calculadora de impacto.
- **Todos (2 h):** auditoría de etiquetas con *confident learning* (cleanlab): lista de los 100 registros más sospechosos para revisión de un analista.

### Semana 3 · 30 nov–4 dic · Modelos clásicos reproducibles (≈ 22 h)

- **R1 (8 h):** árbol, regresión logística y RF sobre el nuevo protocolo; métricas con IC por clusters; calibración inicial.
- **R2 (6 h):** versión 0 del módulo de recomendación con la logística (curvas ICE/PDP por parámetro; búsqueda exhaustiva); informe de soporte por celda.
- **R3 (6 h):** calculadora de impacto v1 (sec. 4.3-A) con rangos; redacción de metodología (secciones 1–3 del documento).
- **Vie 4: Gate 1.** Pasa si: el protocolo está pre-registrado, hay 4 baselines y el pipeline corre de principio a fin con un solo comando.

### Semana 4 · 7–11 dic (4 días hábiles) · Boosting y explicabilidad (≈ 18 h)

- **R1 (8 h):** HistGB, LightGBM, XGBoost y CatBoost con restricciones de monotonía; Optuna en dev (≥ 100 ensayos, mismos presupuestos).
- **R2 (5 h):** SHAP y permutation importance sobre el mejor boosting y la logística; comparación de direcciones con ICE.
- **R3 (5 h):** features derivadas y sus pruebas de no-fuga; comparación pareada por bootstrap entre modelos.

### Semana 5 · 14–18 dic (15-dic mañana ocupada) · Calibración, umbral y recomendador v0 (≈ 20 h)

- **R1 (7 h):** calibración (isotónica/sigmoide agrupada), ECE/Brier; **umbral con cota exacta** (sec. 4.1-H) y decision curve analysis.
- **R2 (8 h):** recomendador sobre el modelo elegido en dev; tarjetas de recomendación; abstención y soporte; pruebas E1 y E4.
- **R3 (5 h):** reunión con guía (jue 17: avance de modelos y diseño del recomendador).
- **Vie 18: Gate 2.** Se **congela el modelo** (tag `modelo-final`). Pasa si: la elección se justificó solo con dev y existe el reporte de calibración.

### Semana 6 · 21–24 dic (capacidad 50 %) · Recomendación completa y test (≈ 12 h)

- **R2 (6 h):** E2 (retrospectiva), E3 (DiCE), E5 (baselines); resultados con IC.
- **R1 (3 h):** evaluación en **test, una sola vez**, mar 22 (tag `test-run`); tabla final de OE1.
- **R3 (3 h):** documento: resultados OE1 y OE2.
- **Mié 23: Gate 3.** Pasa si: los resultados de test están archivados con su tag; se reportan **tal cual salieron** (incluso si no confirman H1/H2).

### Semana 7 · 28–31 dic (capacidad 50 %) · Economía y documento (≈ 12 h)

- **R3 (5 h):** Monte Carlo, tornado, probabilidad de ROI > 0; cierra OE3.
- **R1 (3 h):** reproducibilidad: clonado limpio, ejecución completa, tiempos.
- **R2 (4 h):** documento: discusión, amenazas a la validez, trabajo futuro (dos ideas).

### Semana 8 · 4–8 ene · Integración, deck y ensayos (≈ 22 h)

- **Lun 4 (todos, 4 h):** deck v33 (sec. 8) y matriz de trazabilidad objetivo → método → resultado → conclusión.
- **Mar 5 (todos, 3 h):** ensayo 1 cronometrado y banco de preguntas (sec. 12).
- **Mié 6: congelado.** Documento y deck cerrados; ejecución desde cero en un equipo limpio (R1).
- **Jue 7 (todos, 3 h):** ensayo 2 con el guía o un tercero que haga de jurado.
- **Vie 8:** colchón y revisión final de ortografía, referencias y figuras.
- **Gate 4.**

---

## 6. Banco de ideas creativas (ordenadas por valor / esfuerzo)

| # | Idea | Qué aporta | Cómo (open source) | Esfuerzo |
|---|---|---|---|---|
| 1 | **Etiqueta con margen** ("pasa raspando") | Responde la objeción del profesor sobre pruebas que pasan pero fallan a la mitad; da dirección a la recomendación | Headroom = 1 − p95/objetivo; ordinal con dos cabezas binarias o `mord` | M |
| 2 | **Boosting con monotonía** | Recomendaciones coherentes con la física del sistema | LightGBM/XGBoost/CatBoost `monotone_constraints`; sklearn `monotonic_cst` | S |
| 3 | **Tarjetas de recomendación con abstención** | Resultado concreto y honesto de OE2 | Tabla con ΔP, IC, soporte, razón | M |
| 4 | **Retrospectiva "máquina del tiempo"** | Valida recomendaciones sin ejecutar Gatling | Pares dentro del mismo contexto; τ de Kendall; exactitud por pares | M |
| 5 | **Contrafactuales con DiCE** | Segunda mirada independiente a la búsqueda exhaustiva | `dice-ml` con `features_to_vary` y rangos permitidos | S |
| 6 | **Umbral con garantía estadística** | Convierte el límite del 5 % en un procedimiento y no en una meta | Clopper–Pearson + secuencia fija / Learn-then-Test | M |
| 7 | **Decision curve analysis** | Una figura que dice cuándo conviene el modelo según el costo | Beneficio neto; `dcurves` o fórmula directa | S |
| 8 | **Auditoría de etiquetas con cleanlab** | Entrega a QA una lista priorizada de etiquetas dudosas (el feedback ya pide auditoría continua) | `cleanlab.find_label_issues` con probabilidades fuera de muestra | S |
| 9 | **Monte Carlo del ROI** | De un número único (211 %) a una probabilidad de éxito | Triangulares + NumPy; tornado | S |
| 10 | **Baseline = criterio del analista** | Cierra F10 con un baseline real | Entrevista de 45 min × 2; reglas codificadas | S |
| 11 | **Features de "presión"** | Capturan carga relativa al componente y al objetivo | `carga_total`, `presion`, `nivel_relativo` | S |
| 12 | **Calibración por clusters** | Probabilidades confiables para decidir por costo | `CalibratedClassifierCV` con grupos; ECE/Brier | S |
| 13 | **Protocolo pre-registrado** | Evita la sospecha de "mirar el test" | Hash de Build_Id de test en commit previo | S |
| 14 | **Model card y datasheet** | Formaliza alcance, límites y gobierno | Plantillas Mitchell et al. / Gebru et al. | S |
| 15 | **Matriz de trazabilidad en el deck** | Una lámina que alinea objetivos, método, resultado y conclusión (lo que el profesor echó en falta) | Tabla 3 × 4 | S |

---

## 7. Entregables y estructura del repositorio

```
capstone_copilot/
├─ README.md                  # este plan + cómo reproducir
├─ configs/                   # semillas, protocolo, rangos de supuestos
├─ data/                      # NO se versiona (datos del banco); solo esquema y hash
├─ src/
│  ├─ prep/                   # limpieza, unidad (registro), etiqueta con margen
│  ├─ split/                  # train/dev/test por Build_Id + pruebas de fuga
│  ├─ models/                 # baselines B0–B3, árbol, LR, RF, boosting
│  ├─ evaluate/               # métricas, IC por clusters, calibración, DCA
│  ├─ recommend/              # búsqueda exhaustiva, soporte, abstención, DiCE
│  └─ economics/              # función de costo, Monte Carlo, calculadora
├─ tests/                     # pytest: sin cruce de Build_Id, sin variables posteriores
├─ reports/                   # figuras, tablas, model card, datasheet
└─ Makefile                   # make all = datos → modelos → recomendación → economía
```

**Entregables finales:** documento académico (IMRaD), deck v33, repositorio reproducible con un comando, model card, datasheet, tabla de recomendaciones, matriz de trazabilidad, banco de preguntas.

---

## 8. Rediseño del deck (v33), lámina por lámina

| # | Lámina | Cambio |
|---|---|---|
| 1 | Portada | Sin cambio estructural |
| 2 | Problema | **Agregar impacto económico** (F1): fórmula + rango en pesos |
| 3 | Objetivos | OE1/OE2/OE3 académicos (sec. 3); preguntas e hipótesis |
| 4 | Metodología | Flujo por objetivo (no solo por pasos) |
| 5 | Datos y unidad | **Unidad = registro**, Build_Id = grupo; **conteos** de clases (F7) |
| 6 | EDA | Cada gráfico con n, unidad y significado del p95 (F8) |
| 7 | Variables y fuga | Ex ante vs. posteriores; variables derivadas |
| 8 | Protocolo | **Train/dev/test 70/10/20**, test bloqueado (F9) |
| 9 | Baselines y modelos | B0–B3 y la historia árbol → RF → boosting (F10, F11) |
| 10 | Resultados OE1 | Tabla con IC pareados; calibración |
| 11 | Explicabilidad | SHAP + ICE/PDP; caveats de asociación |
| 12 | Priorización | recall@k, lift y curva de ganancia **como salida de OE1** |
| 13 | Recomendación · método | Matriz carga × resultado, formalización, abstención (F6) |
| 14 | Recomendación · resultados | Tarjeta de ejemplo + pruebas E1–E6 |
| 15 | Evaluación económica | Función de costo, Monte Carlo, DCA (OE3) |
| 16 | Conclusiones | Matriz de trazabilidad; limitaciones; **dos** ideas de trabajo futuro (F13) |

*Anexos:* tuning, ablación, umbral con garantía, validación en Gatling (solo como **trabajo futuro**, F4/F12).

---

## 9. Trabajo futuro (máximo dos ideas, como pidió el profesor)

1. **Diseño secuencial de pruebas (aprendizaje activo / optimización bayesiana):** en lugar de dimensionar por reglas, elegir la **próxima ejecución de Gatling** que más reduce la incertidumbre del modelo sobre el límite de cumplimiento. Beneficio: dimensionar con menos ejecuciones y cerrar el ciclo de validación con un diseño experimental formal.
2. **Gobierno de datos y etiquetado experto continuo, integrado al pipeline (MLOps):** medir el ruido de etiqueta, auditar con QA los casos de mayor sospecha, monitorear deriva y usar el resultado de cada prueba real como retroalimentación. Beneficio: sube el techo del modelo, que hoy depende más de la calidad del dato que del algoritmo.

---

## 10. Riesgos y contingencias

| Riesgo | Prob. | Impacto | Mitigación | Plan B |
|---|---|---|---|---|
| El boosting no supera a RF con IC | Media | Medio | Presupuestos de tuning iguales; diferencias pareadas | Reportarlo como hallazgo: "ensambles más complejos no aportan con este volumen de builds" |
| Señal débil (AUC ≈ 0,6) vuelve poco útil la recomendación | Alta | Alto | Monotonía, features de presión, abstención, soporte mínimo | Posicionar OE2 como **análisis de sensibilidad explicable** (ICE/PDP), con cobertura reportada |
| Pocas configuraciones por contexto (sin soporte) | Media | Alto | Informe de soporte en semana 2 | Agrupar contextos por similitud; reducir el espacio de A |
| Ambigüedad de "no aplica" persiste | Media | Alto | Decisión D2 en semana 1 | Dos variantes de recomendación (subir/bajar) con reglas explícitas |
| Acceso a datos y cifras económicas del banco | Media | Medio | Pedir en semana 2 | Rangos ilustrativos marcados como tales |
| Capacidad en feriados | Alta | Medio | Semanas 6–7 con tareas ligeras | Mover el Monte Carlo a la semana 5 |
| Fecha de defensa anterior a la supuesta | Baja | Alto | Confirmarla el 18-nov | Comprimir semanas 7–8; priorizar OE1 y OE2 |

**Reglas de decisión (go / no-go).**
- Se adopta el boosting solo si ΔROC-AUC pareado tiene IC95 % que excluye 0 contra RF.
- Se publica una recomendación solo si pasa soporte, ΔP ≥ δ y límite inferior > 0.
- Si E2 no supera el azar, el OE2 se presenta como diagnóstico explicable y no como motor prescriptivo.
- **El test no se vuelve a abrir** tras el 22-dic. Si algo falla, se reporta.

---

## 11. Preparación de reuniones

**A. Preguntas para el profesor guía (mié 18-nov).**
1. ¿Los tres OE propuestos cumplen el criterio de "dimensiones comparables"?
2. ¿Cuál es la fecha y el formato de la defensa (documento, paper, ambos)?
3. ¿Aceptan train/dev/test 70/10/20 con validación cruzada agrupada como robustez?
4. ¿Es suficiente la recomendación por optimización discreta con evaluación offline, o esperan algo adicional?
5. ¿Cómo se debe tratar la etiqueta con margen si solo existe en registros completos?
6. ¿Qué nivel de rigor estadístico se espera (bootstrap por clusters, hipótesis pre-registradas)?
7. ¿La evaluación económica con Monte Carlo cabe como OE3?
8. ¿Se prefiere una o dos ideas de trabajo futuro y con qué extensión?

**B. Guía de entrevista a analistas (45 min).**
1. ¿Cómo deciden hoy qué prueba revisar primero? ¿Qué reglas empíricas usan?
2. ¿Qué significa para ustedes que una prueba "no aplique"? ¿Sube o baja la carga?
3. ¿Qué es una prueba que "pasa raspando"? ¿Con qué margen de p95?
4. ¿Qué parámetro suele ajustarse primero y por qué?
5. ¿Cuánto tiempo toma una reejecución (horas del analista, ventana de pruebas)?
6. ¿Qué falla no detectada es la más costosa y cuánto cuesta?
7. ¿Qué campos del contexto (pilar, componente, ambiente, método) se conocen **antes** de ejecutar?
8. ¿Cuántas pruebas por año y qué fracción termina en reejecución?

---

## 12. Defensa: preguntas difíciles que ya sabemos que vienen

| Pregunta | Respuesta corta |
|---|---|
| ¿Qué clasifican: registro o build? | **Registro.** El Build_Id solo agrupa para particionar y para el bootstrap |
| ¿Cómo recomiendan? | Optimización discreta sobre probabilidades calibradas (sec. 4.2-E) |
| ¿Cómo saben que hay que subir y no bajar? | Por la distancia predicha al límite (zona objetivo), no por una regla fija |
| ¿Qué es el baseline? | B2: el criterio del analista codificado; B0: azar a igual capacidad |
| ¿Por qué boosting? | Porque RF fue el primer ensamble; se prueba el siguiente nivel con monotonía y tuning en dev |
| ¿Usaron el test para tunear? | No: dev para hiperparámetros, test una sola vez con hash pre-registrado |
| ¿Hay evidencia de que las recomendaciones sirven? | Offline: monotonía, retrospectiva, estabilidad. La validación online es trabajo futuro |
| ¿Por qué no validan en Gatling? | Requiere ejecuciones autorizadas fuera del alcance; se propone como diseño secuencial |
| ¿El ROI es real? | No; es una proyección ex ante con rangos y probabilidad de ROI > 0 |
| ¿Se puede automatizar la liberación? | Solo si existe un umbral con cota ≤ 5 %; si no existe, se reporta así |

---

## 13. Herramientas (todas open source)

Python 3.11+, pandas, scikit-learn (`StratifiedGroupKFold`, `HistGradientBoosting`, calibración), LightGBM, XGBoost, CatBoost, Optuna, SHAP, `dice-ml`, `cleanlab`, `mord` (opcional), SciPy/NumPy (Clopper–Pearson, Monte Carlo), matplotlib/seaborn, MLflow (seguimiento local), pytest, pre-commit.

---

## 14. Definición de terminado (checklist final)

- [ ] 3 OE académicos, comparables, cada uno con método, resultado y métrica.
- [ ] Ningún OE promete validación online.
- [ ] Unidad de análisis (registro) declarada y probada sin fuga.
- [ ] Conteos de clases por registro y por build en el deck.
- [ ] Protocolo train/dev/test con test usado una vez y hash registrado.
- [ ] Baselines B0–B3 definidos; B2 corresponde al criterio real del analista.
- [ ] Boosting comparado con IC pareado; regresión usada o retirada con justificación.
- [ ] Módulo de recomendación con tarjetas, abstención y evaluación E1–E6.
- [ ] Impacto económico en la lámina 2 con rangos y fuentes.
- [ ] OE3 con Monte Carlo, tornado, break-even y DCA.
- [ ] Máximo dos ideas de trabajo futuro.
- [ ] Ejecución completa desde cero con un comando en un equipo limpio.
- [ ] Dos ensayos cronometrados y banco de preguntas (sec. 12).
