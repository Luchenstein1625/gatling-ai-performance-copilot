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
    title: "6.444 ejecuciones permiten evaluar el problema con un holdout independiente",
    type: "data-quality",
  },
  {
    kicker: "06 · ETL, PREPROCESAMIENTO E INGENIERÍA DE ATRIBUTOS",
    title: "El pipeline evita fugas y convierte resultados Gatling en evidencia auditable",
    type: "comparison",
  },
  {
    kicker: "07 · COMPARACIÓN DE SOLUCIONES IA",
    title: "Random Forest logra el mejor equilibrio para detectar configuraciones que no aplican",
    type: "feature-selection",
  },
  {
    kicker: "08 · ANÁLISIS DE ERROR Y SOBREAJUSTE",
    title: "La brecha train–test exige control: el desempeño es útil, pero no perfecto",
    type: "sensitivity",
  },
  {
    kicker: "09 · PIPELINE DE DECISIÓN POR CAPAS",
    title: "El modelo recomienda; Gatling y el especialista validan el cambio",
    type: "results",
  },
  {
    kicker: "10 · SENSIBILIDAD Y COSTO DEL ERROR",
    title: "Ante la duda, revisar cuesta menos que aprobar una configuración incorrecta",
    type: "case",
  },
  {
    kicker: "11 · RECOMENDACIÓN ÓPTIMA Y EVALUACIÓN ECONÓMICA",
    title: "El cut-off operativo protege la decisión y habilita un beneficio medible",
    type: "impact",
  },
  {
    kicker: "12 · VALIDACIÓN Y TRABAJOS FUTUROS",
    title: "La recomendación solo se aprueba después de una nueva ejecución Gatling",
    type: "implementation",
  },
  {
    kicker: "13 · CONCLUSIONES",
    title: "La POC cumple el objetivo y deja una ruta verificable hacia producción",
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
      <div className="rubric-data-layout">
        <div className="data-hero"><small>INPUT REAL</small><b>6.444</b><span>ejecuciones utilizables de 6.445 filas</span><p>Fuente: <code>resultadoPruebasGatling.txt</code></p></div>
        <div className="class-bars" aria-label="Distribución de la variable objetivo">
          <span>VARIABLE OBJETIVO · APLICABILIDAD DE LA CONFIGURACIÓN</span>
          <div><b>not_applies</b><i><u style={{width:"58.7%"}} /></i><strong>3.781 · 58,7 %</strong></div>
          <div><b>applies</b><i><u className="applies" style={{width:"41.3%"}} /></i><strong>2.663 · 41,3 %</strong></div>
          <p>El desbalance es moderado; se priorizan F1 y recall de <code>not_applies</code>, no solo accuracy.</p>
        </div>
        <div className="split-evidence">
          <div><small>ENTRENAMIENTO</small><b>5.114</b><span>408 Build_Id</span></div>
          <div><small>HOLDOUT</small><b>1.330</b><span>136 Build_Id</span></div>
          <div className="safe"><small>FUGA ENTRE GRUPOS</small><b>0</b><span>Build_Id compartidos</span></div>
        </div>
        <div className="quality-findings"><b>Calidad y límites</b><span><code>apdex</code> contiene referencias Java, no valores numéricos</span><span><code>rating</code> está vacío</span><span>criticidad de negocio no existe y no se inventa</span></div>
        <p className="takeaway"><strong>Conclusión EDA:</strong> el volumen permite comparar modelos; la partición agrupada evita que ejecuciones del mismo build aparezcan en train y test.</p>
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
          <div><strong>Ingesta</strong><span>Lectura del TXT de ancho fijo y normalización de nombres, tipos y categorías</span><span><b>6.444 registros utilizables</b></span></div>
          <div><strong>Control de calidad</strong><span>Se descartan campos vacíos o no numéricos y filas sin etiqueta reproducible</span><span><b>apdex y rating fuera del modelo</b></span></div>
          <div><strong>Prevención de fuga</strong><span>Variables posteriores que revelan directamente la etiqueta no ingresan como predictoras</span><span><b>features disponibles antes de decidir</b></span></div>
          <div className="selected"><strong>Partición y trazabilidad</strong><span>Holdout agrupado por Build_Id; modelo, reglas, métricas y recomendaciones se exportan</span><span><b>0 grupos compartidos</b></span></div>
        </div>
        <div className="etl-evidence">
          <div className="etl-funnel"><b>Flujo auditable</b><span><strong>TXT</strong> real</span><i>→</i><span><strong>ETL</strong> validado</span><i>→</i><span><strong>split</strong> por Build_Id</span><i>→</i><span><strong>artefactos</strong></span></div>
          <div className="null-visual"><b>Variables operacionales</b><span><code>Concurrency</code><i><u style={{width:"82%"}} /></i><strong>carga</strong></span><span><code>Iterations</code><i><u style={{width:"70%"}} /></i><strong>volumen</strong></span><span><code>ResponseTime</code><i><u style={{width:"62%"}} /></i><strong>objetivo</strong></span></div>
        </div>
        <p className="takeaway"><strong>Resultado:</strong> las entradas, transformaciones y decisiones quedan reproducibles; una métrica inválida no se convierte silenciosamente en señal predictiva.</p>
      </div>
    );

  if (type === "feature-selection")
    return (
      <div className="model-comparison-layout">
        <div className="model-table">
          <div className="head"><b>Solución</b><b>Accuracy test</b><b>F1 not_applies</b><b>Recall not_applies</b></div>
          <div><strong>Baseline mayoritario</strong><span>0,5677</span><span>0,7242*</span><span>1,0000*</span></div>
          <div><strong>Árbol de decisión</strong><span>0,6579</span><span>0,6486</span><span>0,5563</span></div>
          <div><strong>Regresión logística</strong><span>0,6895</span><span>0,7165</span><span>0,6914</span></div>
          <div className="winner"><strong>Random Forest</strong><span>0,7256</span><span>0,7446</span><span>0,7046</span></div>
        </div>
        <div className="model-rationale"><small>MODELO SELECCIONADO</small><b>Random Forest</b><p>Maximiza F1 de <code>not_applies</code> entre los modelos entrenados; recall desempata.</p><div><span>+3,6 pp</span><em>accuracy frente a regresión logística</em></div></div>
        <p className="baseline-warning">* El baseline predice siempre <code>not_applies</code>: su recall aparente es alto, pero no detecta ningún caso <code>applies</code>. Por eso no es candidato de selección.</p>
        <p className="takeaway"><strong>Decisión:</strong> Random Forest ofrece el mejor compromiso global sin ocultar la clase operativamente riesgosa.</p>
      </div>
    );

  if (type === "sensitivity")
    return (
      <div className="overfit-layout">
        <div className="train-test-gap"><span>RANDOM FOREST · TRAIN VS TEST</span><div><b>Accuracy</b><i><u style={{width:"83.2%"}} /><u className="test" style={{width:"72.6%"}} /></i><strong>0,8318 → 0,7256</strong></div><div><b>F1 not_applies</b><i><u style={{width:"85.5%"}} /><u className="test" style={{width:"74.5%"}} /></i><strong>0,8547 → 0,7446</strong></div><div><b>Recall not_applies</b><i><u style={{width:"83.6%"}} /><u className="test" style={{width:"70.5%"}} /></i><strong>0,8358 → 0,7046</strong></div></div>
        <div className="gap-reading"><small>LECTURA</small><b>Brecha de ≈ 11 puntos</b><p>Existe sobreajuste moderado. El holdout agrupado entrega una estimación más realista que el desempeño de entrenamiento.</p><div><strong>Control aplicado</strong><span>Separación por Build_Id · 0 solapamiento</span></div><div><strong>Límite</strong><span>Etiquetas derivadas de evidencia, aún sin validación experta independiente</span></div></div>
        <p className="takeaway"><strong>Conclusión:</strong> el modelo es apto para apoyar una revisión humana, no para cambiar configuraciones de forma autónoma.</p>
      </div>
    );

  if (type === "results")
    return (
      <div className="layered-layout">
        <div className="layer-flow"><div><small>CAPA 1</small><b>Aplicabilidad</b><span>applies / not_applies</span></div><Arrow/><div><small>CAPA 2</small><b>Decisión</b><span>review / maintain / upgrade</span></div><Arrow/><div><small>CAPA 3</small><b>Optimización</b><span>cuadrante + parámetros</span></div><Arrow/><div><small>CAPA 4</small><b>Validación</b><span>nueva ejecución Gatling</span></div></div>
        <div className="decision-distribution"><span>HOLDOUT · 1.330 RECOMENDACIONES</span><div className="review"><b>674</b><strong>review</strong><p>50,7 % · conserva configuración</p></div><div><b>383</b><strong>maintain</strong><p>28,8 % · mantiene cuadrante</p></div><div className="upgrade"><b>273</b><strong>upgrade</strong><p>20,5 % · candidato controlado</p></div></div>
        <div className="pipeline-guard"><b>0 cambios automáticos ante review</b><span>Downgrade queda como decisión humana posterior al diagnóstico.</span><strong>100 % de upgrades requieren aprobación</strong></div>
        <p className="takeaway"><strong>Valor:</strong> el modelo no entrega solo una clase; la traduce en una acción, una configuración candidata y un contrato de validación.</p>
      </div>
    );

  if (type === "case")
    return (
      <div className="cost-sensitivity-layout">
        <div className="cost-matrix-v2"><div className="head"><b>Real \ Predicho</b><b>not_applies</b><b>applies</b></div><div><strong>not_applies</strong><span className="good">532 · revisión correcta</span><span className="critical">223 · riesgo de aprobación</span></div><div><strong>applies</strong><span>142 · revisión adicional</span><span className="good">433 · aprobación correcta</span></div></div>
        <div className="cost-priority"><small>COSTO ASIMÉTRICO</small><b>Falso “applies” &gt; falso “not_applies”</b><p>Aprobar una configuración que no aplica puede ocultar una falla real. Enviar un caso válido a review agrega tiempo, pero conserva el control.</p><div><strong>Política</strong><span>incertidumbre, falla o evidencia insuficiente → <b>review</b></span></div></div>
        <div className="threshold-note"><b>Sensibilidad operativa</b><span>El umbral debe priorizar recall de <code>not_applies</code>; el cut-off definitivo se calibrará con costos reales del piloto.</span></div>
        <p className="takeaway"><strong>Recomendación:</strong> usar el modelo como filtro de seguridad y mantener aprobación humana para cualquier cambio.</p>
      </div>
    );

  if (type === "impact")
    return (
      <div className="impact-layout economic-impact">
        <div className="impact-before"><small>SITUACIÓN ACTUAL</small><b>3–48 h + 1–35 h</b><p>Desarrollo y revisión QA; la preparación analítica aún debe medirse por separado.</p></div>
        <Arrow />
        <div className="impact-after"><small>RECOMENDACIÓN ÓPTIMA</small><b>Minutos + validación humana</b><p>Review ante riesgo; maintain si la exigencia es adecuada; upgrade solo con holgura y reejecución.</p></div>
        <div className="economic-model">
          <div><small>BASE HISTÓRICA</small><b>$1.569 MM ÷ 7.003</b><span>≈ $224 mil por atención</span></div>
          <div><small>ALCANCE INICIAL</small><b>144 atenciones/año</b><span>12 atenciones mensuales × 12 meses · ≈ $32,3 MM</span></div>
          <div className="economic-scenario"><small>ESCENARIO PRELIMINAR</small><b>50 % cobertura × 75 % reducción</b><span>Supuestos de adopción y eficiencia · ≈ $12,1 MM potencial/año</span></div>
        </div>
        <p className="economic-note"><strong>Evaluación económica:</strong> ≈ $12,1 MM es beneficio bruto potencial, no ahorro demostrado. El piloto debe medir tiempo antes/después, cobertura real, reejecuciones y costo de falsos “applies”.</p>
      </div>
    );

  if (type === "implementation")
    return (
      <div className="validation-layout">
        <div className="validation-contract"><small>CONTRATO DE VALIDACIÓN ONLINE</small><div><b>1</b><span>Aprobar propuesta <code>upgrade</code></span></div><div><b>2</b><span>Ejecutar nueva prueba Gatling</span></div><div><b>3</b><span>Comparar errores, p95, RPS, éxitos y Estado</span></div><div><b>4</b><span>Aprobar cuadrante o retornar a <code>review</code></span></div></div>
        <div className="validation-status"><span>ESTADO ACTUAL</span><b>pending_new_execution</b><p>La configuración candidata todavía es una recomendación, no evidencia experimental.</p><div><small>ÉXITO</small><strong>0 errores + estado exitoso + sin regresión</strong></div></div>
        <div className="future-work"><b>Trabajos futuros</b><span>Etiquetas expertas independientes</span><span>Calibración económica del cut-off</span><span>Validación temporal y por microservicio</span><span>API, auditoría y monitoreo de drift</span></div>
        <p className="takeaway"><strong>Principio:</strong> si la nueva ejecución falla o es irregular, la propuesta vuelve a review; nunca hay downgrade automático.</p>
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
        <span>OBJETIVO CUMPLIDO</span>
        <p>La POC transforma <b>6.444 resultados Gatling</b> en una recomendación explicable, parámetros candidatos y un proceso de validación controlado.</p>
      </div>
      <div className="next">
        <strong>Entregables verificados</strong>
        <ul>
          <li>Comparación de 3 modelos + baseline</li>
          <li>Pipeline de decisión en cuatro capas</li>
          <li>Cuadrante y parámetros recomendados</li>
          <li>Validación Gatling pendiente y auditable</li>
        </ul>
      </div>
      <div className="closing-line">El valor económico y la configuración óptima se confirmarán en el piloto, no antes.</div>
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
