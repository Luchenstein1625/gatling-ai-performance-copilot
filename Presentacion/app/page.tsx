"use client";

import { useEffect, useState } from "react";
import { PRESENTATION } from "../presentation.config";

const slides = [
  {
    kicker: "CAPSTONE · MAGÍSTER EN INTELIGENCIA ARTIFICIAL · UAI",
    title: "Performance\nIntelligence Copilot",
    subtitle:
      "IA aplicada para automatizar el análisis y acelerar decisiones sobre pruebas de rendimiento",
    type: "cover",
  },
  {
    kicker: "01 · CONTEXTO Y EVOLUCIÓN DEL PROYECTO",
    title: "Del negocio bancario a una decisión de rendimiento explicable",
    type: "business-shift",
  },
  {
    kicker: "02 · PROBLEMA DE NEGOCIO",
    title: "3.960 casos/año en 11 pipelines: el cuello de botella está en la interpretación",
    type: "metrics",
  },
  {
    kicker: "03 · OBJETIVO, ALCANCE Y KPI",
    title: "Acelerar la decisión técnica: de horas a minutos",
    type: "objectives",
  },
  {
    kicker: "04 · METODOLOGÍA Y ARQUITECTURA",
    title: "Un flujo híbrido desde la evidencia hasta la recomendación",
    type: "target-architecture",
  },
  {
    kicker: "05 · DESCRIPCIÓN Y VISUALIZACIÓN",
    title: "Composición y calidad del dataset validado",
    type: "data-quality-summary",
  },
  {
    kicker: "06 · EXPLORACIÓN MULTIVARIABLE",
    title: "Las variables separan la clase y muestran proxies",
    type: "eda-exploration",
  },
  {
    kicker: "07 · ETL, PREPROCESAMIENTO E INGENIERÍA DE ATRIBUTOS",
    title: "ETL e ingeniería de atributos para construir variables auditables",
    type: "comparison",
  },
  {
    kicker: "08 · PRIMER MODELO ENTRENADO",
    title: "Qué aporta hoy el árbol y qué deberá aprender después",
    type: "sensitivity",
  },
  {
    kicker: "09 · EVALUACIÓN DEL MODELO",
    title: "Las variantes cercanas a reglas superan a las operacionales",
    type: "results",
  },
  {
    kicker: "10 · INTEGRACIÓN EN EL PIPELINE",
    title: "La recomendación espera aprobación antes de ejecutar Gatling",
    type: "pipeline-demo",
  },
  {
    kicker: "11 · IMPACTO OPERACIONAL ESPERADO",
    title: "Impacto operacional y evaluación económica preliminar",
    type: "impact",
  },
  {
    kicker: "11 · CONCLUSIONES",
    title: "Una base explicable para decisiones de rendimiento más consistentes",
    type: "closing",
  },
];

const Arrow = () => <span className="arrow" aria-hidden="true">→</span>;

function SlideContent({ type }: { type: string }) {
  if (type === "cover")
    return (
      <div className="cover-layout">
        <div className="cover-copy">
          <div className="signal"><i /><i /><i /><i /></div>
          <p className="subtitle cover-subtitle">IA aplicada para automatizar el análisis y acelerar decisiones sobre pruebas de rendimiento</p>
        </div>
        <div className="authors">
          <span>Grupo 8</span>
          <strong>
            <span>Luis Araya</span>
            <span>Rodrigo González</span>
            <span>Hernán Medina</span>
          </strong>
          <span>Profesor guía: Ahmad Armoush · Agosto 2026</span>
        </div>
      </div>
    );

  if (type === "business-shift")
    return (
      <div className="business-shift-layout">
        <div className="business-map">
          <div className="bank-core">
            <small>NEGOCIO BANCARIO</small>
            <b>Personas y empresas</b>
            <p>Acceden a productos y servicios financieros a través de canales que deben responder de forma continua y estable.</p>
          </div>
          <div className="channel-row" aria-label="Canales y servicios digitales">
            <div><span>WEB</span><b>Canales digitales</b></div>
            <div><span>APP</span><b>Operaciones</b></div>
            <div><span>API</span><b>Servicios integrados</b></div>
          </div>
          <div className="performance-link">
            <span>CAPACIDAD HABILITANTE</span>
            <b>Pruebas de rendimiento</b>
            <p>Permiten medir tiempos de respuesta, errores y capacidad antes de liberar cambios.</p>
          </div>
        </div>

        <div className="shift-story">
          <span className="shift-label">CAMBIO DE ENFOQUE</span>
          <div className="shift-flow">
            <div className="shift-before">
              <small>PRIMERA PRESENTACIÓN</small>
              <b>Predicción de capacidad e infraestructura cloud</b>
              <p>El planteamiento era más amplio que los datos y capacidades demostrables del proyecto.</p>
            </div>
            <Arrow />
            <div className="shift-now">
              <small>PROYECTO REAL</small>
              <b>Copilot para analizar pruebas Gatling</b>
              <p>Integra configuración, resultados e historial para entregar una recomendación explicable.</p>
            </div>
          </div>
          <div className="shift-outcome">
            <span>EVIDENCIA REAL</span>
            <b>Configuración → métricas → análisis → recomendación → validación humana</b>
          </div>
        </div>

        <p className="bridge-line"><strong>Así llegamos al problema:</strong> la prueba puede ejecutarse, pero preparar la evidencia, interpretarla y acordar la siguiente acción sigue requiriendo tiempo y criterio especializado.</p>
      </div>
    );

  if (type === "bank")
    return (
      <div className="bank-layout">
        <div className="bank-intro">
          <span>ORGANIZACIÓN</span>
          <p><strong>Banco de Crédito e Inversiones (BCI)</strong> es una institución financiera chilena que entrega productos y servicios a personas y empresas.</p>
          <p>Sus canales digitales dependen de servicios tecnológicos disponibles, estables y capaces de responder bajo demanda.</p>
        </div>
        <div className="bank-context">
          <div><small>ÁREA DE ORIGEN</small><b>I+DevOps</b><p>Automatización, calidad técnica y apoyo a los equipos de desarrollo.</p></div>
          <div><small>CAPACIDAD CLAVE</small><b>Pruebas de rendimiento</b><p>Permiten observar tiempos de respuesta, errores y capacidad antes de liberar cambios.</p></div>
          <div><small>NECESIDAD</small><b>Decisiones consistentes</b><p>La evidencia de rendimiento debe traducirse en una recomendación clara y trazable.</p></div>
        </div>
        <p className="takeaway"><strong>Performance Intelligence Copilot</strong> analiza configuraciones, métricas e historial para comprender cómo responde cada componente ante distintos niveles de carga y recomendar mantener, revisar o evaluar un aumento controlado, siempre con validación humana.</p>
      </div>
    );

  if (type === "lessons")
    return (
      <div className="lessons-layout">
        <div className="scope-before"><small>ENFOQUE INICIAL</small><b>Capacidad genérica para pruebas de rendimiento</b><p>Incluía infraestructura y múltiples decisiones, pero no contábamos con todas esas fuentes ni con una frontera demostrable.</p></div>
        <Arrow />
        <div className="scope-after"><small>ALCANCE AFINADO</small><b>Estimar la siguiente decisión de una prueba de estrés</b><p>Usamos configuración, resultados e historial para recomendar mantener, revisar o evolucionar la exigencia.</p></div>
        <div className="evidence-unlock"><span>¿POR QUÉ CAMBIÓ?</span><p>Con más fuentes identificamos que el cuello de botella está en <strong>coordinar insumos, interpretar resultados y aplicar criterios consistentes dentro del SLA</strong>.</p></div>
        <p className="takeaway"><strong>Aprendizaje central:</strong> el nuevo alcance parte de más evidencia y menos supuestos, conectando la POC con la fricción operativa real.</p>
      </div>
    );

  if (type === "metrics")
    return (
      <div className="metric-layout">
        <div className="big-stat"><b>3.960</b><span>casos de prueba / año</span><p><strong>La operación procesa 330 casos mensuales en 11 pipelines.</strong> El costo recurrente de diseño y ejecución alcanza 4,8 UF por prueba, acumulando 19.008 UF anuales en esfuerzo operativo.</p></div>
        <div className="metric-side">
          <div><b>330/mes</b><span>casos Gatling en 11 pipelines</span></div>
          <div><b>86 %</b><span>del costo en automatización y mantención</span></div>
        </div>
        <div className="metric-impact">
          <div>
            <small>VOLUMEN OPERATIVO</small>
            <b>3.960</b>
            <span>casos / año · 330 × 12 meses · 11 pipelines activos</span>
          </div>
          <div>
            <small>COSTO ANUAL ESTIMADO</small>
            <b>19.008 UF</b>
            <span>operación directa (diseño + ejecución) · ≈ $718 MM/año</span>
          </div>
          <div>
            <small>COSTO PROMEDIO / CASO</small>
            <b>4,8 UF</b>
            <span>diseño 2,4 UF + ejecución 2,4 UF · ≈ $181 mil por prueba</span>
          </div>
          <div className="metric-placeholder">
            <small>DESGLOSE DE ESFUERZO</small>
            <b>34,5 UF</b>
            <span className="metric-placeholder-label">ciclo completo / caso</span>
            <span>automatización 19,8 UF + mantención 9,9 UF = 86 % del total</span>
          </div>
        </div>

      </div>
    );

  if (type === "process")
    return (
      <div className="process-wrap">
        <div className="process-line">
          {["Ticket", "Planificar", "Preparar insumos", "Ejecutar", "Analizar", "Aprobar"].map((x, i) => (
            <div className={i === 4 ? "hot-step" : ""} key={x}><span>{i + 1}</span><strong>{x}</strong>{i < 5 && <Arrow />}</div>
          ))}
        </div>
        <div className="split-copy">
          <p><strong>El flujo actual</strong> cruza servicio transversal y equipo online: ticket, capacidad, scripts, datos de prueba, consumo de APIs, resultados y visto bueno.</p>
          <p><strong>El punto crítico</strong> está en cerrar insumos, interpretar la ejecución y dejar lista la decisión siguiente.</p>
        </div>
      </div>
    );

  if (type === "decision")
    return (
      <div className="decision-grid">
        <div className="decision-card maintain"><small>RECOMENDACIÓN 01</small><b>MAINTAIN</b><p>La evidencia permite conservar la configuración actual.</p></div>
        <div className="decision-card review"><small>RECOMENDACIÓN 02</small><b>REVIEW</b><p>Un especialista debe revisar la configuración antes de continuar.</p></div>
        <div className="decision-card evolve"><small>RECOMENDACIÓN 03</small><b>EVOLVE</b><p>La estabilidad histórica permite evaluar un aumento controlado de carga.</p></div>
        <div className="guardrail"><span>PRINCIPIO DE CONTROL</span><strong>Review tiene prioridad. Evolve propone +10 % y siempre exige validación humana.</strong></div>
      </div>
    );

  if (type === "objectives")
    return (
      <div className="objective-modern-layout">
        <div className="objective-modern-top">
          <article className="objective-modern-hero">
            <small>OBJETIVO GENERAL</small>
            <p>Integrar configuración, resultados e historial Gatling para recomendar la siguiente acción técnica con trazabilidad y validación humana.</p>
          </article>
          <div className="objective-modern-cards">
            <article>
              <span>01</span>
              <b>Pipeline confiable</b>
              <p>Ingesta, validación y normalización reproducible.</p>
            </article>
            <article>
              <span>02</span>
              <b>Motor explicable</b>
              <p>Recomendación maintain/review/evolve con reglas y modelo interpretable.</p>
            </article>
            <article>
              <span>03</span>
              <b>Evaluación controlada</b>
              <p>Comparación con baseline y control explícito de sobreajuste.</p>
            </article>
          </div>
        </div>
        <div className="objective-modern-kpis">
          <div className="objective-kpi-table" aria-label="Tabla de cumplimiento de KPI">
            <div className="head"><b>KPI</b><b>Meta</b><b>Resultado (operational_core)</b><b>Estado</b></div>
            <div><span>Cobertura</span><span>&gt;= 95 %</span><strong>96,6 % (28/29)</strong><em>Cumple</em></div>
            <div><span>Macro-F1 operacional</span><span>&gt;= 0,55</span><strong>0,5987</strong><em>Cumple</em></div>
            <div><span>Balanced accuracy operacional</span><span>&gt;= 0,55</span><strong>0,62</strong><em>Cumple</em></div>
            <div><span>Desv. Macro-F1 operacional</span><span>&lt;= 0,20</span><strong>0,1738</strong><em>Cumple</em></div>
            <div><span>Mejora Macro-F1 vs baseline</span><span>&gt;= 0,15</span><strong>+0,1820 pp</strong><em>Cumple</em></div>
          </div>
          <p className="kpi-note">Las variantes cercanas a las reglas (all_features, without_assertions) alcanzaron 1,00, pero <code>operational_core</code> se usa como resultado principal por excluir proxies cercanos a la etiqueta.</p>
        </div>
        <div className="objective-modern-guardrail"><span>ALCANCE POC</span><strong>Entrega recomendación explicable (maintain/review/evolve). No modifica ni ejecuta pruebas sin validación humana.</strong></div>
      </div>
    );

  if (type === "data-quality-summary")
    return (
      <div className="quality-summary-layout">
        <p className="quality-summary-note">La muestra útil es pequeña: 28 registros. El CSV no trae microservicio explícito, por lo que la procedencia se reconstruye desde el árbol de orígenes de ejemplo.</p>

        <div className="quality-summary-grid">
          <div className="quality-summary-left">
            <div className="quality-summary-strip compact" aria-label="Resumen de composición y calidad">
              <article>
                <small>EMBUDO</small>
                <b>29 → 28</b>
                <p>1 ejecución fue omitida por duplicado.</p>
              </article>
              <article>
                <small>CLASE</small>
                <b>20 / 8</b>
                <p>La muestra está desbalanceada.</p>
              </article>
              <article>
                <small>NULOS</small>
                <b>1 columna</b>
                <p><code>p90_response_time_ms</code> quedó vacía.</p>
              </article>
            </div>

            <div className="quality-variable-table" aria-label="Resumen de variables principales">
            <div className="head"><b>Variable</b><b>Pregunta que responde</b><b>Rol</b></div>
            <div><code>error_rate_percent</code><span>Señal de falla operacional</span><em>Señal</em></div>
            <div><code>p95_response_time_ms</code><span>Latencia del 95 % de solicitudes</span><em>Señal</em></div>
            <div><code>sla_margin_ms</code><span>Brecha entre p95 y SLA</span><em>Derivada</em></div>
            <div><code>assertions_failed</code><span>Reglas técnicas incumplidas</span><em>Señal</em></div>
            <div><code>warning_count</code><span>Advertencias del análisis</span><em>Proxy</em></div>
            <div><code>recommendation_action</code><span>Salida: maintain, review o evolve</span><em>Etiqueta</em></div>
          </div>
          </div>

          <div className="quality-summary-chart" aria-label="Distribución de orígenes de ejemplo por microservicio">
            <img src="/graficos-lamina-5-microservicios.png" alt="Distribución de 30 carpetas de entrada por microservicio de ejemplo" />
            <p><strong>Fuente:</strong> árbol <code>app/examples/input/sources</code>. Se usan 30 carpetas de entrada repartidas en 11 microservicios; el CSV final sigue siendo de 28 registros.</p>
          </div>
        </div>


      </div>
    );

  if (type === "eda-exploration")
    return (
      <div className="eda-exploration-layout">
        <p className="eda-exploration-note">Cada visual responde una pregunta distinta. Con n=28, la exploración es descriptiva y sirve para fundamentar la POC, no para probar un universo distinto.</p>

        <div className="eda-exploration-graphic" aria-label="Exploración multivariable con boxplots, distribución y correlaciones">
          <img src="/graficos-lamina-5-multivariable-v2.png" alt="Exploración multivariable de la muestra validada con boxplots, histograma de assertions_failed y matriz de correlaciones" />
        </div>

        <div className="eda-exploration-insights">
          <article>
            <small>01 · ERROR RATE</small>
            <b>review concentra los picos altos</b>
            <p><code>review</code> se mueve hacia valores mucho más altos; <code>evolve</code> se mantiene cerca de cero.</p>
          </article>
          <article>
            <small>02 · SLA MARGIN</small>
            <b>review incumple con más holgura</b>
            <p>El margen <code>p95 - SLA</code> se desplaza a positivo en <code>review</code>.</p>
          </article>
          <article>
            <small>03 · ASSERTIONS FAILED</small>
            <b>las fallas se concentran en pocos casos</b>
            <p>La señal es asimétrica y confirma que las reglas pesan, aunque aparecen poco.</p>
          </article>
          <article>
            <small>04 · CORRELACIONES</small>
            <b>hay coherencia interna, no causalidad</b>
            <p>Las variables proxy se mueven juntas; eso ayuda al modelo y también lo condiciona.</p>
          </article>
        </div>


      </div>
    );

  if (type === "alternatives")
    return (
      <div className="alternatives-layout">
        <div className="alternatives-table">
          <div className="head"><b>Alternativa</b><b>Qué resuelve bien</b><b>Límite frente al problema</b><b>Mejora que aporta la POC</b></div>
          <div><strong>Gatling · JMeter · k6 · NeoLoad</strong><span>Ejecutan pruebas y entregan métricas.</span><span>No traducen esa evidencia en una acción.</span><b>Agrega una decisión explicable.</b></div>
          <div><strong>APM · dashboards · observabilidad</strong><span>Correlacionan señales y visualizan comportamiento.</span><span>Requieren interpretación humana.</span><b>Transforma observación en recomendación.</b></div>
          <div><strong>Revisión experta manual</strong><span>Aporta contexto técnico y criterio especializado.</span><span>Es más lenta y variable.</span><b>Estandariza la salida.</b></div>
          <div className="selected"><strong>Performance Intelligence Copilot</strong><span>Integra evidencia, reglas e historial técnico.</span><span>No reemplaza esas piezas.</span><b>Las une en una recomendación trazable.</b></div>
        </div>
        <p className="takeaway"><strong>Resumen:</strong> la POC agrega la decisión reproducible que hoy falta entre ejecutar, observar y actuar.</p>
      </div>
    );

  if (type === "target-architecture")
    return (
      <div className="target-arch">
        <div className="target-row">
          <div><small>01 · ENTRADAS</small><b>Configuración + métricas + historial</b></div><Arrow />
          <div><small>02 · PREPARACIÓN</small><b>Normalización + etiquetado</b></div><Arrow />
          <div className="implemented"><small>03 · INTELIGENCIA</small><b>Reglas + árbol ML + evaluación histórica</b></div><Arrow />
          <div className="implemented"><small>04 · SALIDA POC</small><b>Recomendación explicable</b></div>
        </div>
        <div className="target-row future">
          <div><small>05 · INTEGRACIÓN OBJETIVO</small><b>API de recomendaciones</b></div><Arrow />
          <div><small>06 · EXPERIENCIA OBJETIVO</small><b>Interfaz de visualización y aprobación</b></div>
        </div>
        <div className="arch-notes" aria-label="Metodología y protocolo de evaluación">
          <div className="arch-note-card">
            <small>METODOLOGÍA EXPLÍCITA</small>
            <ul>
              <li>Variables de entrada: configuración, métricas, assertions y warning_count; la etiqueta objetivo es <code>recommendation_action</code>.</li>
              <li>Modelo base: <code>DecisionTreeClassifier</code> con <code>max_depth=4</code>, <code>class_weight="balanced"</code> y <code>random_state=42</code>.</li>
              <li>Las reglas expertas generan la etiqueta; no son una variable de entrada. <code>operational_core</code> excluye assertions y warning proxies para medir generalización operativa.</li>
            </ul>
          </div>
          <div className="arch-note-card">
            <small>PROTOCOLO CONTROLADO</small>
            <ul>
              <li>30 particiones holdout estratificadas reproducibles con <code>StratifiedShuffleSplit</code>, <code>test_size=0,25</code> y <code>random_state=42</code>.</li>
              <li>Comparación entre <code>all_features</code>, <code>without_assertions</code> y <code>operational_core</code> para separar réplica de reglas, ablación de proxies y lectura operativa.</li>
              <li>Métricas: baseline mayoritario, accuracy, balanced accuracy, Macro-F1 e IC95 sobre las repeticiones.</li>
            </ul>
          </div>
        </div>
        <div className="arch-legend"><span><i />Implementado en la POC</span><span><i />Evolución objetivo</span></div>

      </div>
    );

  if (type === "comparison")
    return (
      <div className="comparison-layout comparison-modern">
        <div className="comparison-left">
          <div className="comparison-summary-strip compact" aria-label="Resumen de muestra y control de calidad">
            <article>
              <small>EMBUDO</small>
              <b>29 → 28</b>
              <p>Se omitió 1 ejecución duplicada; la muestra útil queda en 28 registros.</p>
            </article>
            <article>
              <small>DISTRIBUCIÓN</small>
              <b>20 / 8</b>
              <p>El corte final está desbalanceado, por eso se evalúa de forma estratificada.</p>
            </article>
            <article>
              <small>NULOS</small>
              <b>1 columna</b>
              <p><code>p90_response_time_ms</code> quedó vacía en todas las filas y se excluyó del entrenamiento.</p>
            </article>
          </div>

          <div className="comparison-table comparison-table-modern" aria-label="Control de variables y fuga de información">
            <div className="head"><b>Control</b><b>Qué se hizo</b><b>Por qué importa</b></div>
            <div><strong>Outliers</strong><span>No se aplicó un detector automático. Los extremos se revisaron en la exploración y se conservaron porque son ejecuciones reales y el dataset es pequeño.</span><span>Evita perder señal operativa y mantiene representatividad.</span></div>
            <div><strong>Fuga de información</strong><span>Se excluyen <code>schema_version</code>, <code>metrics_scope</code> y la etiqueta <code>recommendation_action</code>. En <code>operational_core</code> también se quitan <code>assertions_*</code> y <code>warning_count</code>.</span><span>Impide que el modelo vea metadatos o proxies demasiado cercanos a la decisión.</span></div>
            <div><strong>Historial comparable</strong><span>Es la misma estructura de columnas, el mismo esquema y el mismo pipeline de preparación para comparar ejecuciones sin cambiar la regla de lectura.</span><span>Permite comparar corridas con una base homogénea y trazable.</span></div>
          </div>
        </div>

        <div className="comparison-right">
          <div className="etl-prep-panel">
            <small>PREPROCESAMIENTO REAL ANTES DE ENTRENAR</small>
            <div className="etl-step"><span>01</span><div><b>Filtrar columnas válidas</b><p>Se usan solo las variables no metadata y no etiqueta. Luego se elimina la columna vacía <code>p90_response_time_ms</code>.</p></div></div>
            <div className="etl-step"><span>02</span><div><b>Imputar faltantes</b><p>Las numéricas usan mediana; las categóricas usan el valor <code>__missing__</code>.</p></div></div>
            <div className="etl-step"><span>03</span><div><b>Codificar categóricas</b><p><code>load_type</code> y <code>assertions_all_passed</code> pasan por <code>OneHotEncoder</code>. No se usa escalamiento.</p></div></div>
            <div className="etl-step"><span>04</span><div><b>Entrenar el árbol</b><p>El modelo final es <code>DecisionTreeClassifier</code> con <code>max_depth=4</code>, <code>class_weight="balanced"</code> y <code>random_state=42</code>.</p></div></div>
            <div className="etl-note"><strong>Margen SLA:</strong> <code>sla_margin_ms = p95_response_time_ms - strictest_response_time_target_ms</code>. Si el resultado es positivo, el p95 supera el SLA; si es negativo, cumple.</div>
          </div>
        </div>


      </div>
    );

  if (type === "sensitivity")
    return (
      <div className="sensitivity-layout">
        <div className="cost-matrix">
          <div className="head"><b>Evidencia</b><b>Qué permite afirmar</b><b>Qué no permite afirmar</b></div>
          <div><strong>Variantes cercanas a reglas</strong><span>all_features y without_assertions llegan a Macro-F1 = 1,00 y balanced accuracy = 1,00 en 30 particiones</span><b>Eso sí reproduce etiquetas</b></div>
          <div><strong>Señales operacionales</strong><span>operational_core baja a Macro-F1 = 0,5987 y balanced accuracy = 0,62</span><b>La señal operativa sola es más débil</b></div>
          <div className="critical"><strong>Lectura metodológica</strong><span>Las variables cercanas al motor de reglas reproducen las etiquetas; al restringirlas a señales operacionales, el desempeño cae</span><b>No debe leerse como reproducción fuerte de reglas expertas</b></div>
        </div>
        <div className="feature-panel">
          <span>APORTE DEL MACHINE LEARNING · CONVERGENCIA CON REGLAS EXPERTAS, NO SUSTITUCIÓN</span>
          <div className="importance-card">
            <small>IMPORTANCIA APRENDIDA POR EL ÁRBOL · operational_core (sin proxies)</small>
            <div className="importance-table" aria-label="Importancia de variables del árbol operational_core">
              <div className="head"><b>Variable</b><b>Importancia</b><b>Rol operacional</b></div>
              <div><code>error_rate_percent</code><strong>0,50</strong><span>Porcentaje de solicitudes fallidas en la ejecución</span></div>
              <div><code>min_response_time_ms</code><strong>0,50</strong><span>Tiempo mínimo de respuesta; señala degradación base</span></div>
            </div>
            <p style={{margin:'5px 0 0',fontSize:'clamp(7px,.6vw,10px)',color:'#6b8292'}}>Fuente: <code>historical_model_explanation.json</code> · importancia Gini del árbol entrenado sobre el perfil operational_core (18 variables, sin assertions ni warning_count).</p>
          </div>
          <div className="ml-value"><small>HALLAZGO DE ESTA MUESTRA</small><strong>Sin proxies de reglas, el árbol se apoya en <code>error_rate_percent</code> y <code>min_response_time_ms</code> con igual importancia.</strong><p>Esto sugiere que la tasa de error y la latencia mínima son las señales operativas más informativas disponibles para separar las clases en esta muestra.</p></div>
          <div className="ml-value future"><small>SIGUIENTE VALIDACIÓN</small><strong>Desacoplar etiquetas y señales operacionales</strong><p>Separar entrenamiento/prueba por microservicio y usar etiquetas expertas independientes para medir generalización real.</p></div>
        </div>

      </div>
    );

  if (type === "results")
    return (
      <div className="results-layout">
        <div className="result-hero evidence-first">
          <small>CONCLUSIÓN DEL EXPERIMENTO</small>
          <strong>La comparación separa señales cercanas a reglas de señales operacionales</strong>
          <p>Las variantes con variables cercanas al motor de reglas alcanzan 1,00; al restringirlas a señales operacionales, el desempeño desciende a Macro-F1 0,5987 y balanced accuracy 0,62.</p>
        </div>
        <div className="result-proof">
          <div><small>DATOS EVALUADOS</small><b>28 ejecuciones</b><span>20 evolve · 8 review</span></div>
          <div><small>PROTOCOLO</small><b>30 particiones</b><span>holdout estratificado · 21/7 · random_state 42</span></div>
          <div><small>OPERATIONAL_CORE</small><b>Macro‑F1 0,5987</b><span>balanced accuracy 0,62 · review F1 0,3968 · std 0,1738</span></div>
          <div><small>BASELINE MAYORITARIO</small><b>Macro‑F1 0,4167</b><span>accuracy 0,7143 · balanced acc. 0,50 · review F1 0,00</span></div>
        </div>
        <div className="evaluation-graphic" aria-label="Comparación de variantes y brecha de sobreajuste">
          <img className="evaluation-chart" src="/graficos-lamina-9-v2.png" alt="Evaluación comparativa con etiquetas explícitas: all_features y without_assertions en 1,0000 (con proxies), operational_core en 0,5987 (sin assertions ni warning proxies)" />
          <div className="evaluation-legend-cards" aria-label="Leyenda de interpretación de barras">
            <span><b>1,0000</b> all_features y without_assertions: comportamiento estable en las 30 particiones</span>
            <span><b>0,5987</b> operational_core: caída al usar solo señales operacionales</span>
          </div>
        </div>
        <div className="evidence-boundary">
          <div><small>SÍ DEMUESTRA</small><b>Estabilidad por partición</b><span>all_features y without_assertions mantienen accuracy, balanced accuracy, Macro-F1 y review F1 en 1,00.</span></div>
          <div><small>NO DEMUESTRA TODAVÍA</small><b>Generalización operacional</b><span>operational_core cae a accuracy 0,7143, balanced accuracy 0,62 y review F1 0,3968.</span></div>
        </div>

      </div>
    );

  if (type === "pipeline-demo")
    return (
      <div className="pipeline-demo-layout">

        {/* ── Flujo del proyecto: de Gatling a la recomendación ── */}
        <div className="pdl-flow" aria-label="Flujo del proyecto desde Gatling hasta la recomendación">
          <div className="pdl-step">
            <div className="pdl-step-icon pdl-icon-src">G</div>
            <small>ENTRADA</small>
            <b>Resultados Gatling</b>
            <p>global_stats.json · assertions.json · YAML configuración</p>
          </div>
          <div className="pdl-step-arrow">→</div>
          <div className="pdl-step">
            <div className="pdl-step-icon pdl-icon-etl">ETL</div>
            <small>NORMALIZACIÓN</small>
            <b>Ingesta y validación</b>
            <p>28 ejecuciones importadas · p90 excluida · imputación mediana</p>
          </div>
          <div className="pdl-step-arrow">→</div>
          <div className="pdl-step">
            <div className="pdl-step-icon pdl-icon-ml">ML</div>
            <small>MODELO</small>
            <b>Árbol de decisión</b>
            <p>max_depth=4 · operational_core · error_rate + min_response_time</p>
          </div>
          <div className="pdl-step-arrow">→</div>
          <div className="pdl-step pdl-step-highlight">
            <div className="pdl-step-icon pdl-icon-rec">★</div>
            <small>SALIDA</small>
            <b>Recomendación</b>
            <p>maintain · review · evolve con evidencia explicable y trazabilidad</p>
          </div>
        </div>

        {/* ── Pipeline Azure DevOps: dónde se integra ── */}
        <div className="pipeline-stages" aria-label="Pipeline Azure DevOps con gate del Copilot">
          <div className="ps-stage ps-done">
            <div className="ps-icon">✓</div>
            <div className="ps-info"><small>Build Artifact</small><b>Completado</b><span>2m 12s</span></div>
          </div>
          <div className="ps-arrow">→</div>
          <div className="ps-stage ps-done">
            <div className="ps-icon">✓</div>
            <div className="ps-info"><small>Deploy to Dev</small><b>Completado</b><span>3m 48s</span></div>
          </div>
          <div className="ps-arrow">→</div>
          <div className="ps-stage ps-active">
            <div className="ps-icon ps-spin">⟳</div>
            <div className="ps-info"><small>Karate Smoke</small><b>En ejecución</b><span>6m 45s</span></div>
          </div>
          <div className="ps-arrow">→</div>
          <div className="ps-stage ps-copilot ps-pulse">
            <div className="ps-icon ps-copilot-icon">★</div>
            <div className="ps-info">
              <small>Copilot Gate</small>
              <b>REVIEW — aprobación QA</b>
              <span className="ps-waiting-dot">● En espera</span>
            </div>
          </div>
          <div className="ps-arrow ps-arrow-dim">→</div>
          <div className="ps-stage ps-pending">
            <div className="ps-icon">○</div>
            <div className="ps-info"><small>loadTestingNuevo</small><b>No iniciado</b><span>Gatling</span></div>
          </div>
          <div className="ps-arrow ps-arrow-dim">→</div>
          <div className="ps-stage ps-pending">
            <div className="ps-icon">○</div>
            <div className="ps-info"><small>Deploy to QA</small><b>No iniciado</b><span>—</span></div>
          </div>
        </div>


      </div>
    );

  if (type === "impact")
    return (
      <div className="impact-layout economic-impact">
        <div className="impact-before"><small>ESCENARIO A · ACTUAL</small><b>4,8 UF / prueba</b><p>Diseño 2,4 UF + Ejecución 2,4 UF por caso (≈ $181 mil CLP). Costo recurrente que el Copilot busca reducir.</p></div>
        <Arrow />
        <div className="impact-after"><small>ESCENARIO B · CON COPILOT</small><b>Minutos + validación humana</b><p>La preparación analítica y la recomendación se automatizan; QA recibe evidencia explicable para aprobar con mayor rapidez.</p></div>
        <div className="economic-model">
          <div><small>BASE HISTÓRICA / ANUAL</small><b>19.008 UF</b><span>3.960 casos/año × 4,8 UF · ≈ $718,5 MM CLP/año</span></div>
          <div><small>ALCANCE DE COBERTURA</small><b>3.960 casos/año</b><span>11 pipelines × 330 casos/mes · diseño 2,4 UF + ejecución 2,4 UF</span></div>
          <div className="economic-scenario"><small>ESCENARIO PRELIMINAR</small><b>7.128 UF / año</b><span>19.008 UF × 50 % cobertura × 75 % reducción · ≈ $269,4 MM CLP/año</span></div>
        </div>

      </div>
    );

  if (type === "implementation")
    return (
      <div className="implementation-layout">
        <div className="implementation-flow">
          <div><span>01</span><b>Integrar fuentes</b><p>Resultados, configuraciones e historial.</p></div>
          <div><span>02</span><b>Persistir y versionar</b><p>Ejecuciones, etiquetas y modelos.</p></div>
          <div><span>03</span><b>Exponer y aprobar</b><p>API, interfaz, evidencia y validación humana.</p></div>
          <div><span>04</span><b>Evolucionar con control</b><p>YAML propuesto, diff, aprobación, monitoreo, auditoría y reversión.</p></div>
        </div>
        <div className="implementation-compare"><b>Aporte demostrado</b><span>pipeline reproducible desde los archivos de entrada hasta la recomendación</span><b>Control</b><span>explicación trazable y aprobación humana</span></div>
        <div className="implementation-proof">
          <div><small>ENTRADA REAL</small><b>YAML + resultados Gatling</b></div>
          <div><small>SALIDA REAL</small><b>Maintain · Review · Evolve</b></div>
          <div><small>EVIDENCIA</small><b>Reglas activadas + explicación</b></div>
        </div>
        <p className="takeaway"><strong>Siguiente validación:</strong> medir en un piloto el tiempo de análisis y las reejecuciones antes y después de incorporar el Copilot.</p>
      </div>
    );

  if (type === "value")
    return (
      <div className="value-layout">
        <div className="value-points">
          {[
            ["Hoy", "Recomendación explicable: maintain, review o evolve."],
            ["Siguiente", "Generar un YAML propuesto con parámetros ajustados."],
            ["Control", "Mostrar diff, validar esquema y solicitar aprobación humana."],
            ["Después", "Reemplazar o ejecutar la prueba aprobada con auditoría y reversión."],
          ].map(([a,b]) => <div key={a}><b>{a}</b><p>{b}</p></div>)}
        </div>
        <div className="value-kpis"><b>Controles</b><span>validación de esquema</span><span>diff antes/después</span><span>versionado</span><span>aprobación y reversión</span></div>
        <p className="takeaway"><strong>Límite actual:</strong> la POC finaliza en la recomendación. El YAML modificado, su reemplazo y la ejecución controlada corresponden a etapas posteriores.</p>
      </div>
    );

  if (type === "roadmap")
    return (
      <div className="evolution-roadmap">
        <div className="roadmap-current-stage"><small>HOY · POC IMPLEMENTADA</small><b>Recomendación explicable</b><p>Maintain · Review · Evolve, evidencia, explicación y plan de acción.</p></div><Arrow />
        <div className="next-stage"><small>SIGUIENTE ETAPA</small><b>Prueba lista para ejecutar</b><p>Preparar el artefacto ajustado para revisión según la recomendación.</p></div><Arrow />
        <div className="future-stage"><small>EVOLUCIÓN POSTERIOR</small><b>Reemplazar si se aprueba</b><p>Versionado, aprobación y reemplazo controlado.</p></div>
        <div className="roadmap-controls"><span>Validación de esquema</span><span>Diff antes/después</span><span>Aprobación humana</span><span>Auditoría y reversión</span></div>
        <p className="takeaway"><strong>Límite actual:</strong> la POC no ejecuta pruebas automáticamente.</p>
      </div>
    );

  if (type === "questions")
    return (
      <div className="questions-layout">
        <div className="roadmap">
          {[
            ["01", "Problema", "La revisión sigue dependiendo del especialista."],
            ["02", "Diferencia", "La POC ordena la evidencia y propone la salida."],
            ["03", "Resultado", "La recomendación queda preparada para revisión humana."],
            ["04", "Siguiente paso", "Generar la prueba lista para ejecutar si se aprueba."],
          ].map(([n, title, copy]) => (
            <div className="roadmap-item" key={n}>
              <span>{n}</span>
              <div><b>{title}</b><p>{copy}</p></div>
            </div>
          ))}
        </div>
        <div className="questions-panel">
          <span>IDEA DE CIERRE</span>
          <blockquote>La solución no reemplaza al especialista: organiza la evidencia y deja clara la siguiente acción.</blockquote>
          <strong>Gracias</strong>
          <p>Preguntas</p>
        </div>
      </div>
    );

  return (
    <div className="closing-layout">
      <div className="closing-claim">
        <span>CONTRIBUCIÓN</span>
        <p>La POC transforma resultados Gatling en datos estructurados y demuestra que un árbol interpretable puede aprender las etiquetas del motor experto cuando utiliza variables cercanas a esas reglas. Al restringirlo a señales operacionales, <b>supera el baseline</b>, aunque su generalización aún debe validarse con nuevos datos y etiquetas independientes.</p>
      </div>
      <div className="next">
        <strong>Siguiente validación</strong>
        <ul>
          <li>Validar las recomendaciones con especialistas</li>
          <li>Ampliar el histórico con nuevos casos etiquetados</li>
          <li>Medir tiempo de análisis y reejecuciones en un piloto</li>
        </ul>
      </div>
      <div className="closing-line">La generalización deberá validarse con nuevos datos y revisión experta.</div>
    </div>
  );
}

export default function Home() {
  const [index, setIndex] = useState(0);
  const [overview, setOverview] = useState(false);
  const [printMode, setPrintMode] = useState(false);

  const go = (next: number) => setIndex(Math.max(0, Math.min(slides.length - 1, next)));

  useEffect(() => {
    setPrintMode(new URLSearchParams(window.location.search).get("print") === "1");
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") go(index + 1);
      if (e.key === "ArrowLeft" || e.key === "PageUp") go(index - 1);
      if (e.key.toLowerCase() === "o") setOverview((v) => !v);
      if (e.key === "Escape") setOverview(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [index]);

  const renderSlide = (slide: (typeof slides)[number], slideIndex: number) => (
    <main className={`deck slide-${slide.type}`} key={`${slide.type}-${slideIndex}`}>
      <section className="slide" aria-label={`Diapositiva ${slideIndex + 1} de ${slides.length}`}>
        <div className="brand"><span>BCI</span><i />UAI</div>
        <p className="kicker">{slide.kicker}</p>
        <h1>{slide.title.split("\n").map((t,i)=><span key={t}>{t}{i === 0 && slide.title.includes("\n") && <br/>}</span>)}</h1>
        {slide.subtitle && slide.type !== "cover" && <p className="subtitle">{slide.subtitle}</p>}
        <SlideContent type={slide.type} />
        <footer><span>{PRESENTATION.name} · v{PRESENTATION.version}</span><b>{String(slideIndex + 1).padStart(2,"0")} / {slides.length}</b></footer>
      </section>
    </main>
  );

  if (printMode)
    return <div className="print-deck">{slides.map(renderSlide)}</div>;

  if (overview)
    return (
      <main className="overview">
        <header><b>Performance Intelligence Copilot</b><button onClick={() => setOverview(false)}>Cerrar vista general</button></header>
        <div className="overview-grid">
          {slides.map((s, i) => <button key={s.title} onClick={() => {setIndex(i); setOverview(false);}}><span>{String(i + 1).padStart(2,"0")}</span><b>{s.title.replace("\n"," ")}</b></button>)}
        </div>
      </main>
    );

  const slide = slides[index];
  return (
    <main className={`deck slide-${slide.type}`}>
      <section className="slide" aria-label={`Diapositiva ${index + 1} de ${slides.length}`}>
        <div className="brand"><span>BCI</span><i />UAI</div>
        <p className="kicker">{slide.kicker}</p>
        <h1>{slide.title.split("\n").map((t,i)=><span key={t}>{t}{i === 0 && slide.title.includes("\n") && <br/>}</span>)}</h1>
        {slide.subtitle && slide.type !== "cover" && <p className="subtitle">{slide.subtitle}</p>}
        <SlideContent type={slide.type} />
        <footer><span>{PRESENTATION.name} · v{PRESENTATION.version}</span><b>{String(index + 1).padStart(2,"0")} / {slides.length}</b></footer>
      </section>
      <nav aria-label="Navegación de diapositivas">
        <button onClick={() => go(index - 1)} disabled={index === 0} aria-label="Anterior">←</button>
        <button className="overview-btn" onClick={() => setOverview(true)}>Vista general</button>
        <a
          className="pdf-btn"
          href="/Performance-Intelligence-Copilot-latest.pdf"
          onClick={(e) => {
            e.currentTarget.href = `/Performance-Intelligence-Copilot-latest.pdf?t=${Date.now()}`;
          }}
          download={`Performance-Intelligence-Copilot-v${PRESENTATION.version}.pdf`}
        >
          Descargar PDF · v{PRESENTATION.version}
        </a>
        <button onClick={() => go(index + 1)} disabled={index === slides.length - 1} aria-label="Siguiente">→</button>
      </nav>
      <div className="progress" style={{width:`${((index + 1) / slides.length) * 100}%`}} />
    </main>
  );
}
