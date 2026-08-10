"use client";

import { useEffect, useState } from "react";
import { PRESENTATION } from "../presentation.config";

const slides = [
  {
    kicker: "CAPSTONE · MAGÍSTER EN INTELIGENCIA ARTIFICIAL · UAI",
    title: "Performance\nIntelligence Copilot",
    subtitle:
      "Sistema híbrido y explicable para apoyar decisiones en pruebas de rendimiento",
    type: "cover",
  },
  {
    kicker: "01 · CONTEXTO Y EVOLUCIÓN DEL PROYECTO",
    title: "Del negocio bancario a una decisión de rendimiento explicable",
    type: "business-shift",
  },
  {
    kicker: "02 · PROBLEMA DE NEGOCIO",
    title: "El cuello de botella no es ejecutar la prueba: es preparar, interpretar y aprobar",
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
    title: "Composición y calidad del dataset disponible",
    type: "data-quality",
  },
  {
    kicker: "06 · ETL, PREPROCESAMIENTO E INGENIERÍA DE ATRIBUTOS",
    title: "ETL e ingeniería de atributos para construir variables auditables",
    type: "comparison",
  },
  {
    kicker: "07 · SELECCIÓN DE CARACTERÍSTICAS",
    title: "Panorama de señales evaluadas y límites de la muestra",
    type: "feature-selection",
  },
  {
    kicker: "08 · PRIMER MODELO ENTRENADO",
    title: "Qué aporta hoy el árbol y qué deberá aprender después",
    type: "sensitivity",
  },
  {
    kicker: "09 · EVALUACIÓN DEL MODELO",
    title: "El árbol reproduce H6, pero aún no demuestra generalización",
    type: "results",
  },
  {
    kicker: "10 · VALIDACIÓN EN UN CASO REAL",
    title: "La falla actual prevalece sobre un buen historial",
    type: "case",
  },
  {
    kicker: "11 · IMPACTO OPERACIONAL ESPERADO",
    title: "Impacto operacional y evaluación económica preliminar",
    type: "impact",
  },
  {
    kicker: "12 · IMPLEMENTACIÓN Y EVOLUCIÓN",
    title: "De la POC a una capacidad productiva y controlada",
    type: "implementation",
  },
  {
    kicker: "13 · CONCLUSIONES",
    title: "Una base explicable para decisiones de rendimiento más consistentes",
    type: "closing",
  },
];

const Arrow = () => <span className="arrow" aria-hidden="true">→</span>;

function SlideContent({ type }: { type: string }) {
  if (type === "cover")
    return (
      <div className="cover-layout">
        <div>
          <div className="signal"><i /><i /><i /><i /></div>
          <p className="cover-note">POC funcional · Motor experto + Machine Learning</p>
          <p className="cover-version">Versión {PRESENTATION.version} · Agosto 2026</p>
        </div>
        <div className="authors">
          <span>Grupo 8</span>
          <strong>Luis Araya · Rodrigo González · Hernán Medina</strong>
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
        <div className="big-stat"><b>3–48 h</b><span>desarrollo de la prueba según complejidad</span><p><strong>Una prueba de rendimiento</strong> somete un sistema a carga controlada para medir tiempos de respuesta, errores y capacidad antes de liberar un cambio.</p></div>
        <div className="metric-side">
          <div><b>Línea base por medir</b><span>preparación analítica e interpretación de resultados</span></div>
          <div><b>1–35 h</b><span>revisión y aprobación QA</span></div>
          <div><b>12/mes</b><span>6 tareas por sprint</span></div>
        </div>
        <div className="economic-context">
          <span><b>7.003</b> atenciones anuales del servicio</span>
          <span><b>$1.569 MM</b> costo anual informado</span>
          <span><b>≈ $224 mil</b> costo promedio ponderado por atención</span>
        </div>
        <p className="business-risk"><strong>Impacto para el proyecto:</strong> reducir el tiempo dedicado a consolidar evidencia y entregar una recomendación técnica trazable antes de aprobar la siguiente prueba.</p>
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
      <div className="objective-layout">
        <blockquote>Automatizar el análisis de configuraciones, resultados e historial para generar en minutos una recomendación explicable sobre la siguiente prueba de estrés.</blockquote>
        <div className="objective-list">
          {[
            ["01", "Entrada", "YAML, JSON e historial"],
            ["02", "Entregable", "recomendación + explicación"],
            ["03", "KPI técnico", "Macro-F1 y balanced accuracy"],
            ["04", "KPI operativo", "Preparación analítica y recomendación: línea base por medir → meta en minutos"],
          ].map(([n, a, b]) => <div key={n}><span>{n}</span><p><strong>{a}</strong><br />{b}</p></div>)}
        </div>
        <div className="guardrail"><span>ALCANCE POC</span><strong>Termina en Maintain · Review · Evolve. No modifica ni ejecuta pruebas sin validación humana.</strong></div>
      </div>
    );

  if (type === "data-quality")
    return (
      <div className="data-layout">
        <div className="predictor-charts" aria-label="Relación entre variables predictoras y recomendación">
          <img className="historical-charts" src="/graficos-lamina-6.png" alt="Tasa de error y margen de p95 respecto del SLA para las 28 ejecuciones, agrupadas por maintain y review" />
          <div className="dataset-funnel"><b>59</b><span>detectadas</span><i>→</i><b>29</b><span>completas</span><i>→</i><b>28</b><span>finales · 20 maintain / 8 review</span></div>
        </div>
        <div className="variable-dictionary" aria-label="Diccionario de variables principales">
          <div className="head"><b>Variable</b><b>Descripción operacional</b><b>Rol</b></div>
          <div><code>error_rate_percent</code><span>Porcentaje de solicitudes fallidas</span><em>Predictora</em></div>
          <div><code>p95_response_time_ms</code><span>Tiempo bajo el cual finaliza el 95 % de las solicitudes</span><em>Predictora</em></div>
          <div><code>sla_margin_ms</code><span>Diferencia entre p95 observado y SLA; positivo = incumplimiento</span><em>Derivada</em></div>
          <div><code>assertions_failed</code><span>Cantidad de criterios técnicos incumplidos</span><em>Predictora</em></div>
          <div><code>warning_count</code><span>Advertencias generadas durante el análisis</span><em>Posible proxy</em></div>
          <div><code>recommendation_action</code><span>Decisión maintain o review generada por H6</span><em>Objetivo</em></div>
        </div>
        <div className="eda-insights" aria-label="Insights principales del análisis exploratorio">
          <div>
            <small>COMPOSICIÓN FINAL</small>
            <b>20 maintain frente a 8 review</b>
            <p>La muestra final contiene <strong>28 casos</strong> y presenta desbalance entre las dos clases disponibles.</p>
          </div>
          <div>
            <small>ALCANCE DEL ANÁLISIS</small>
            <b>Evidencia exploratoria</b>
            <p>El desbalance <strong>71,4 % / 28,6 %</strong> justificó usar Macro-F1 y balanced accuracy.</p>
          </div>
        </div>
        <p className="takeaway"><strong>Nota:</strong> análisis exploratorio sobre 28 ejecuciones. Las asociaciones observadas son preliminares y no demuestran generalización.</p>
        <p className="predictor-scope"><strong>Universo evaluado:</strong> carga/concurrencia, TPS, volumen de solicitudes e historial comparable también se probaron como predictoras, pero no aportaron señal al árbol (importancia 0,00). El diccionario destaca las variables con importancia o relevancia metodológica.</p>
      </div>
    );

  if (type === "data")
    return (
      <div className="data-layout">
        <div className="file-stack"><div style={{"--i":0} as any}>configuracion.yaml</div><div style={{"--i":1} as any}>parametros.yaml</div><div style={{"--i":2} as any}>metricas.json</div><div style={{"--i":3} as any}>historial.csv</div></div>
        <div className="data-table">
          <div><span>Entradas</span><p>Configuración, parámetros, resultados e historial técnico existentes, pero dispersos entre equipos y artefactos.</p></div>
          <div><span>Preparación</span><p>Validación de esquema, resolución de parámetros, normalización de métricas y representación común.</p></div>
          <div><span>Reutilización</span><p>La evidencia alimenta reglas, entrenamiento supervisado, comparación histórica y reporte explicable.</p></div>
          <div><span>Aporte</span><p>Convierte evidencia fragmentada en un insumo trazable y reutilizable para decidir la siguiente acción.</p></div>
        </div>
        <p className="takeaway">Antes de recomendar, el sistema ordena la evidencia técnica y la deja lista para análisis y decisión.</p>
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
        <div className="arch-legend"><span><i />Implementado en la POC</span><span><i />Evolución objetivo</span></div>
        <p className="takeaway">La POC termina hoy en una recomendación y artefactos trazables. API e interfaz se muestran como evolución, no como capacidades ya implementadas.</p>
      </div>
    );

  if (type === "comparison")
    return (
      <div className="comparison-layout">
        <div className="comparison-table">
          <div className="head"><b>Etapa ETL</b><b>Tratamiento aplicado</b><b>Resultado</b></div>
          <div><strong>Ingesta</strong><span>59 carpetas de ejecución detectadas; se exigieron configuración, parámetros y resultados Gatling legibles</span><span><b>29 ejecuciones completas</b> formaron el dataset inicial de 29 × 27</span></div>
          <div><strong>Validación de filas</strong><span>Cada fila debía representar una ejecución terminada, cumplir el esquema, tener tipos válidos y una recomendación reproducible</span><span><b>1 ejecución abortada excluida</b>; quedaron 28 registros validados y 0 duplicados</span></div>
          <div><strong>Nulos y atípicos</strong><span><b>1 columna excluida:</b> p90_response_time_ms, con 28 de 28 valores nulos; las demás variables utilizadas quedaron sin nulos</span><span><b>0 % de filas eliminado por outliers:</b> los extremos se conservaron como posibles señales de degradación</span></div>
          <div className="selected"><strong>Ingeniería de atributos</strong><span>Se crean: cumplimiento de SLA, assertions fallidas, margen respecto del SLA e historial comparable</span><span>Predictoras derivadas con sentido técnico y de negocio</span></div>
        </div>
        <div className="etl-evidence">
          <div className="etl-funnel"><b>Embudo</b><span><strong>59</strong> detectadas</span><i>→</i><span><strong>29</strong> completas</span><i>→</i><span><strong>28</strong> válidas</span></div>
          <div className="null-visual" aria-label="Visualización de valores nulos"><b>Nulos por columna</b><span><code>p90_response_time_ms</code><i><u /></i><strong>28/28</strong></span><span><code>Variables utilizadas</code><i><u className="zero" /></i><strong>0/28</strong></span></div>
        </div>
        <p className="takeaway"><strong>Validación final:</strong> 59 detectadas → 29 completas → 28 válidas. Los nulos de p90 eliminaron una columna, no registros; los outliers se conservaron como evidencia técnica.</p>
      </div>
    );

  if (type === "feature-selection")
    return (
      <div className="feature-selection-layout">
        <div className="signal-landscape">
          <span>MAPA DE VARIABLES CANDIDATAS</span>
          <div className="signal-group"><b>Carga aplicada</b><p>Concurrencia · TPS · volumen de solicitudes</p><em>Contexto de ejecución</em></div>
          <div className="signal-group"><b>Respuesta del sistema</b><p>Tasa de error · p95 · margen respecto del SLA</p><em>Desempeño observado</em></div>
          <div className="signal-group caution"><b>Criterios derivados</b><p>Assertions fallidas · warning_count</p><em>Posible dependencia de H6</em></div>
          <div className="signal-group"><b>Memoria histórica</b><p>Historial comparable y comportamiento previo</p><em>Contexto temporal</em></div>
          <p className="landscape-note">Todas se evaluaron como predictoras. En esta muestra, carga, TPS, volumen e historial no agregaron separación al árbol entrenado; esto no permite concluir que sean irrelevantes en otros datos.</p>
        </div>
        <div className="selection-reading">
          <div className="class-separation">
            <span>COMPOSICIÓN DE LA MUESTRA</span>
            <div><b>20</b><i><u /></i><p><strong>maintain</strong> · 71,4 %</p></div>
            <div className="review"><b>8</b><i><u /></i><p><strong>review</strong> · 28,6 %</p></div>
            <p>El desbalance justifica Macro‑F1 y balanced accuracy; no autoriza extrapolar el patrón a nuevos servicios.</p>
          </div>
          <div className="selection-conclusion">
            <small>HALLAZGO DE ESTA MUESTRA</small>
            <strong>Las etiquetas coinciden con criterios derivados del mismo motor que las generó.</strong>
            <p><code>assertions_failed</code> fue la señal utilizada por este árbol y <code>warning_count</code> puede actuar como proxy. Se reporta como dependencia potencial, no como variable universalmente decisiva.</p>
          </div>
          <p className="proxy-note">Próxima validación: excluir conjuntamente variables de assertions y warnings, y separar entrenamiento/prueba por microservicio.</p>
        </div>
      </div>
    );

  if (type === "sensitivity")
    return (
      <div className="sensitivity-layout">
        <div className="cost-matrix">
          <div className="head"><b>Evidencia</b><b>Qué permite afirmar</b><b>Qué no permite afirmar</b></div>
          <div><strong>Baseline mayoritario</strong><span>Referencia mínima frente al desbalance de clases</span><b>No evalúa señales</b></div>
          <div><strong>10 holdouts estratificados</strong><span>Estabilidad interna en particiones de 21 train / 7 test</span><b>No reemplaza datos externos</b></div>
          <div className="critical"><strong>Árbol de decisión</strong><span>Reproduce las etiquetas históricas de H6 en la muestra disponible</span><b>No prueba generalización</b></div>
        </div>
        <div className="feature-panel">
          <span>APORTE DEL MACHINE LEARNING · CONVERGENCIA CON H6, NO SUSTITUCIÓN</span>
          <div className="ml-value"><small>HOY · POC</small><strong>Auditar la relación entre señales y decisiones históricas</strong><p>El árbol hace explícitas dependencias y posibles fugas de información.</p></div>
          <div className="ml-value future"><small>CON MÁS HISTÓRICO</small><strong>Detectar combinaciones que las reglas actuales no capturan</strong><p>Requiere etiquetas expertas independientes, más servicios y validación temporal.</p></div>
        </div>
        <p className="takeaway"><strong>Alcance:</strong> el experimento confirma reproducibilidad interna y revela dependencia de la fuente de etiquetas. El valor futuro del ML debe probarse con señales independientes y casos que las reglas actuales no resuelvan por sí solas.</p>
      </div>
    );

  if (type === "results")
    return (
      <div className="results-layout">
        <div className="result-hero evidence-first">
          <small>CONCLUSIÓN DEL EXPERIMENTO</small>
          <strong>La evaluación mide fidelidad a H6 dentro de una muestra pequeña</strong>
          <p>El desempeño observado es consistente en las particiones evaluadas, pero las etiquetas y algunas variables comparten la misma fuente de verdad.</p>
        </div>
        <div className="result-proof">
          <div><small>DATOS EVALUADOS</small><b>28 ejecuciones</b><span>20 maintain · 8 review</span></div>
          <div><small>PROTOCOLO</small><b>10 semillas</b><span>holdout estratificado · 21/7</span></div>
          <div><small>RESULTADO OBSERVADO</small><b>Macro‑F1 1,0000</b><span>DE 0,0000 · solo en esta muestra</span></div>
          <div><small>BASELINE MAYORITARIO</small><b>0,4167</b><span>Macro‑F1 · siempre predice maintain</span></div>
        </div>
        <div className="evidence-boundary">
          <div><small>SÍ DEMUESTRA</small><b>Fidelidad interna</b><span>Reproduce de forma estable las decisiones históricas generadas por H6.</span></div>
          <div><small>NO DEMUESTRA TODAVÍA</small><b>Generalización</b><span>No hay etiquetas expertas independientes, servicios externos ni ablación libre de proxies.</span></div>
        </div>
        <p className="result-message"><strong>Próximo experimento decisivo:</strong> ablación conjunta de assertions y warnings, partición agrupada por microservicio y etiquetas expertas independientes. Solo entonces podrá evaluarse si el modelo aporta generalización adicional a las reglas.</p>
      </div>
    );

  if (type === "case")
    return (
      <div className="case-flow">
        <div><small>ENTRADA</small><b>Cuadrante 5</b><span>Assertions fallidas</span></div><Arrow />
        <div><small>REGLAS EXPERTAS</small><b>review</b><span>criterio de seguridad</span></div><Arrow />
        <div><small>ÁRBOL DE DECISIÓN</small><b>review</b><span>concordancia: true</span></div><Arrow />
        <div className="case-final"><small>EVALUACIÓN HISTÓRICA</small><b>review</b><span>evolve bloqueado</span></div>
        <p>Una validación fallida activa la <strong>revisión de configuración</strong>. La estabilidad histórica nunca puede elevar la carga cuando la ejecución actual presenta incumplimientos.</p>
      </div>
    );

  if (type === "impact")
    return (
      <div className="impact-layout economic-impact">
        <div className="impact-before"><small>ESCENARIO A · ACTUAL</small><b>3–48 h + 1–35 h</b><p>Desarrollo de la prueba y posterior revisión QA. El tiempo específico de preparación analítica se medirá en el piloto.</p></div>
        <Arrow />
        <div className="impact-after"><small>ESCENARIO B · CON COPILOT</small><b>Minutos + validación humana</b><p>La preparación analítica y la recomendación se automatizan; QA recibe evidencia explicable para revisar y aprobar con mayor rapidez.</p></div>
        <div className="economic-model">
          <div><small>BASE HISTÓRICA</small><b>$1.569 MM ÷ 7.003</b><span>≈ $224 mil por atención</span></div>
          <div><small>ALCANCE INICIAL</small><b>144 atenciones/año</b><span>12 atenciones mensuales × 12 meses · ≈ $32,3 MM</span></div>
          <div className="economic-scenario"><small>ESCENARIO PRELIMINAR</small><b>50 % cobertura × 75 % reducción</b><span>Supuestos de adopción y eficiencia · ≈ $12,1 MM potencial/año</span></div>
        </div>
        <p className="economic-note"><strong>Supuestos:</strong> 144 atenciones = 12 mensuales × 12 meses; 50 % es cobertura inicial estimada y 75 % es una meta preliminar de reducción del esfuerzo abordado. Deben validarse en un piloto antes de considerar ahorro efectivo.</p>
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
        <p>La POC transforma resultados Gatling en datos estructurados y entrena un primer modelo capaz de <b>reproducir las recomendaciones del motor de reglas</b> sobre la muestra disponible.</p>
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
        {slide.subtitle && <p className="subtitle">{slide.subtitle}</p>}
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
        {slide.subtitle && <p className="subtitle">{slide.subtitle}</p>}
        <SlideContent type={slide.type} />
        <footer><span>{PRESENTATION.name} · v{PRESENTATION.version}</span><b>{String(index + 1).padStart(2,"0")} / {slides.length}</b></footer>
      </section>
      <nav aria-label="Navegación de diapositivas">
        <button onClick={() => go(index - 1)} disabled={index === 0} aria-label="Anterior">←</button>
        <button className="overview-btn" onClick={() => setOverview(true)}>Vista general</button>
        <a className="pdf-btn" href={`/Performance-Intelligence-Copilot-v${PRESENTATION.version}.pdf`} download={`Performance-Intelligence-Copilot-v${PRESENTATION.version}.pdf`}>Descargar PDF · v{PRESENTATION.version}</a>
        <button onClick={() => go(index + 1)} disabled={index === slides.length - 1} aria-label="Siguiente">→</button>
      </nav>
      <div className="progress" style={{width:`${((index + 1) / slides.length) * 100}%`}} />
    </main>
  );
}
