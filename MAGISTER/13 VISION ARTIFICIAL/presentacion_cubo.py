# presentacion_cubo.py
import json
import os
from flask import Flask, render_template_string

app = Flask(__name__, static_folder="static", static_url_path="/static")

# --- Slides config ---
# Replace image URLs with local ones later (e.g., "/static/slide1.jpg").
slides = [
    {
        "type": "image",
        "title": "Bienvenidos",
        "subtitle": "Deck moderno en 3D · oscuro y elegante",
        "image_url": "https://images.unsplash.com/photo-1522199755839-a2bacb67c546?q=80&w=1889&auto=format&fit=crop",
    },
    {
        "type": "image",
        "title": "Visión",
        "subtitle": "Diseño limpio y potente",
        "image_url": "https://images.unsplash.com/photo-1482192505345-5655af888cc4?q=80&w=1887&auto=format&fit=crop",
    },
    {
        "type": "image",
        "title": "Estrategia",
        "subtitle": "Foco en claridad, innovación y estilo",
        "image_url": "https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d?q=80&w=1935&auto=format&fit=crop",
    },
    {
        "type": "chart-line",  # Interactive line chart (hover + hover-animate)
        "title": "Crecimiento",
        "subtitle": "Línea con animación suave al pasar el mouse",
    },
    {
        "type": "image",
        "title": "Arquitectura",
        "subtitle": "Sistemas sólidos, simples y escalables",
        "image_url": "https://images.unsplash.com/photo-1526392060635-9d6019884377?q=80&w=1975&auto=format&fit=crop",
    },
    {
        "type": "image",
        "title": "Casos de Uso",
        "subtitle": "Experiencias reales y medibles",
        "image_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=1950&auto=format&fit=crop",
    },
    {
        "type": "chart-bar",  # Interactive bar chart (hover + jitter animation)
        "title": "Resultados",
        "subtitle": "Barras que reaccionan al mouse",
    },
    {
        "type": "image",
        "title": "Equipo",
        "subtitle": "Talento, colaboración y cultura",
        "image_url": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?q=80&w=1935&auto=format&fit=crop",
    },
    {
        "type": "image",
        "title": "Roadmap",
        "subtitle": "Ejecución gradual, impacto sostenido",
        "image_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1974&auto=format&fit=crop",
    },
    {
        "type": "image",
        "title": "Gracias",
        "subtitle": "¿Preguntas?",
        "image_url": "https://images.unsplash.com/photo-1516912481808-3406841bd33c?q=80&w=1974&auto=format&fit=crop",
    },
]

TEMPLATE = r"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Presentación 3D · Cubo</title>
  <!-- Plotly for charts -->
  <script src="https://cdn.plot.ly/plotly-2.29.1.min.js"></script>
  <style>
    :root {
      --bg: #0a0a0a;
      --panel: rgba(30, 30, 30, 0.85);
      --stroke: rgba(255,255,255,0.12);
      --txt: #eaeaea;
      --muted: #a1a1aa;
      --accent: #ffffff;
      --radius: 22px;
      --transition: cubic-bezier(0.22, 1, 0.36, 1);
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0; background: var(--bg); color: var(--txt);
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
    }
    .vignette {
      position: fixed; inset: 0;
      pointer-events: none;
      background: radial-gradient(circle at 50% 40%, rgba(255,255,255,0.07), transparent 55%);
      mix-blend-mode: overlay; opacity: 0.3;
    }
    .grain {
      position: fixed; inset: 0; pointer-events: none; mix-blend-mode: overlay; opacity: .16;
      background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2"/></filter><rect width="100%" height="100%" filter="url(%23n)" opacity="0.35"/></svg>');
      background-size: cover;
    }
    .wrap {
      max-width: 1200px; margin: 0 auto; padding: 20px 24px;
    }
    header {
      display: flex; align-items: center; justify-content: space-between;
      margin: 10px 0 18px;
    }
    header .title { font-weight: 600; letter-spacing: .3px; color: #d4d4d8; }
    header .count { color: var(--muted); font-size: 14px; }
    .stage {
      position: relative; height: 70vh; border-radius: var(--radius);
      perspective: 1200px; overflow: visible;
    }
    .shadow {
      position: absolute; left: 50%; transform: translateX(-50%);
      bottom: -30px; width: 68%; height: 90px; filter: blur(30px);
      background: rgba(0,0,0,.7); border-radius: 1000px; z-index: 0;
    }
    .cube {
      position: relative; width: 100%; height: 100%;
      transform-style: preserve-3d;
      transition: transform 900ms var(--transition);
      will-change: transform;
      z-index: 1;
    }
    .face {
      position: absolute; inset: 0; border-radius: var(--radius);
      overflow: hidden; border: 1px solid var(--stroke);
      background: linear-gradient(180deg, rgba(40,40,40,.95), rgba(18,18,18,.9) 60%);
      box-shadow: 0 10px 40px rgba(0,0,0,.6);
      transform-style: preserve-3d;
    }
    .face-content {
      position: relative; z-index: 3; height: 100%;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      padding: clamp(24px, 5vw, 40px); text-align: center; user-select: none;
    }
    .bg-img {
      position: absolute; inset: 0; z-index: 1;
      background-size: cover; background-position: center; filter: saturate(0.9) brightness(0.75);
      transform: translateZ(-1px) scale(1.01);
    }
    .fx-overlay {
      position: absolute; inset: 0; z-index: 2;
      background: radial-gradient(1000px 400px at 50% -20%, rgba(255,255,255,.12), transparent 60%);
      mix-blend-mode: overlay;
    }
    h2 { font-size: clamp(28px, 4vw, 48px); margin: 0 0 10px; letter-spacing: .2px; }
    p.lead { color: var(--muted); font-size: clamp(16px, 2vw, 20px); margin: 8px 0 0; }
    .controls {
      position: absolute; inset: 0; display: flex; align-items: center; justify-content: space-between; pointer-events: none;
    }
    .btn {
      pointer-events: auto; border: 1px solid var(--stroke); color: var(--txt);
      background: rgba(255,255,255,.06); backdrop-filter: blur(6px);
      padding: 12px 16px; border-radius: 16px; cursor: pointer;
      transition: background 200ms ease;
      margin: 0 6px;
      user-select: none;
    }
    .btn:hover { background: rgba(255,255,255,.12); }
    .dots { display: flex; gap: 8px; align-items: center; justify-content: center; margin-top: 14px; }
    .dot { width: 10px; height: 10px; border-radius: 999px; background: rgba(255,255,255,.35); border: 1px solid var(--stroke); cursor: pointer; }
    .dot.active { background: var(--accent); }
    .footer-actions { display: flex; gap: 10px; align-items: center; justify-content: center; margin-top: 12px; }
    .button {
      appearance: none; border: 1px solid var(--stroke); color: var(--txt);
      padding: 10px 18px; border-radius: 14px; background: rgba(255,255,255,.08);
      cursor: pointer;
    }
    .button.primary { background: #fff; color: #000; }
    /* Chart container inside a face */
    .chart-frame {
      width: min(900px, 92%);
      height: min(460px, 58vh);
      background: rgba(20,20,20,.6);
      border: 1px solid var(--stroke);
      border-radius: 16px;
      padding: 8px;
      box-shadow: inset 0 0 30px rgba(0,0,0,.25);
    }
    @media (max-width: 640px) {
      .stage { height: 62vh; }
      .chart-frame { height: 46vh; }
    }
  </style>
</head>
<body>
  <div class="vignette"></div>
  <div class="grain"></div>
  <div class="wrap">
    <header>
      <div class="title">Deck 3D · Transición tipo cubo</div>
      <div class="count"><span id="count"></span></div>
    </header>

    <div class="stage" id="stage">
      <div class="shadow"></div>
      <div class="cube" id="cube"></div>
      <div class="controls">
        <button class="btn" id="prev" aria-label="Anterior">◀</button>
        <button class="btn" id="next" aria-label="Siguiente">▶</button>
      </div>
    </div>

    <div class="dots" id="dots"></div>
    <div class="footer-actions">
      <button class="button" id="backBtn">Atrás</button>
      <button class="button primary" id="nextBtn">Siguiente</button>
    </div>
  </div>

  <script>
    const slides = {{ slides_json | safe }};
    const cube = document.getElementById('cube');
    const countEl = document.getElementById('count');
    const dotsEl = document.getElementById('dots');
    const prevBtn = document.getElementById('prev');
    const nextBtn = document.getElementById('next');
    const backBtn = document.getElementById('backBtn');
    const nextBtn2 = document.getElementById('nextBtn');
    const depth = 900;
    const half = depth / 2;
    let index = 0;
    let touchStartX = null;

    function clampIndex(i) { const n = slides.length; return ((i % n) + n) % n; }

    // Build dots
    function buildDots() {
      dotsEl.innerHTML = '';
      slides.forEach((_, i) => {
        const d = document.createElement('div');
        d.className = 'dot' + (i === index ? ' active' : '');
        d.addEventListener('click', () => { index = i; render(); });
        dotsEl.appendChild(d);
      });
    }

    // Build 4 faces reused as a cube
    function ensureFaces() {
      if (cube.children.length) return;
      for (let face = 0; face < 4; face++) {
        const f = document.createElement('div');
        f.className = 'face';
        f.dataset.face = face;
        cube.appendChild(f);
      }
    }

    function faceTransform(face) {
      const angle = face * 90;
      return `rotateY(${angle}deg) translateZ(${half}px)`;
    }

    function slideHTML(slide, faceId) {
      if (slide.type === 'image') {
        const bg = slide.image_url || '';
        return `
          <div class="bg-img" style="background-image:url('${bg}')"></div>
          <div class="fx-overlay"></div>
          <div class="face-content">
            <h2>${slide.title || ''}</h2>
            <p class="lead">${slide.subtitle || ''}</p>
          </div>
        `;
      }
      if (slide.type === 'chart-line') {
        return `
          <div class="face-content">
            <h2>${slide.title || ''}</h2>
            <p class="lead">${slide.subtitle || ''}</p>
            <div class="chart-frame"><div id="chart-line-${faceId}" style="width:100%;height:100%;"></div></div>
          </div>
        `;
      }
      if (slide.type === 'chart-bar') {
        return `
          <div class="face-content">
            <h2>${slide.title || ''}</h2>
            <p class="lead">${slide.subtitle || ''}</p>
            <div class="chart-frame"><div id="chart-bar-${faceId}" style="width:100%;height:100%;"></div></div>
          </div>
        `;
      }
      return `<div class="face-content"><h2>${slide.title || ''}</h2><p class="lead">${slide.subtitle || ''}</p></div>`;
    }

    // Render/refresh faces content based on the current index
    function renderFaces() {
      const faces = Array.from(cube.children);
      faces.forEach((f, face) => {
        const s = slides[clampIndex(index + face)];
        f.style.transform = faceTransform(face);
        f.innerHTML = slideHTML(s, face + '-' + Date.now());
      });
    }

    // Render cube rotation and UI
    function render() {
      ensureFaces();
      renderFaces();
      const angle = index * 90;
      cube.style.transform = `translateZ(-${half}px) rotateY(${angle}deg)`;
      countEl.textContent = `${index + 1} / ${slides.length}`;
      buildDotsActive();
      // After transition ends, (re)draw chart if slide is chart
      setTimeout(() => renderActiveCharts(), 920);
    }

    function buildDotsActive() {
      const dots = Array.from(dotsEl.children);
      dots.forEach((d, i) => d.classList.toggle('active', i === index));
    }

    function next() { index = clampIndex(index + 1); render(); }
    function prev() { index = clampIndex(index - 1); render(); }

    // Keyboard
    window.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') next();
      if (e.key === 'ArrowLeft') prev();
    });

    // Touch swipe
    const stage = document.getElementById('stage');
    stage.addEventListener('touchstart', (e) => { touchStartX = e.touches[0].clientX; }, { passive: true });
    stage.addEventListener('touchend', (e) => {
      if (touchStartX == null) return;
      const dx = e.changedTouches[0].clientX - touchStartX;
      if (Math.abs(dx) > 40) { if (dx < 0) next(); else prev(); }
      touchStartX = null;
    });

    prevBtn.addEventListener('click', prev);
    nextBtn.addEventListener('click', next);
    backBtn.addEventListener('click', prev);
    nextBtn2.addEventListener('click', next);

    // --- Charts ---
    let animTimer = null;

    function renderActiveCharts() {
      const s = slides[index];
      if (!s) return;
      if (animTimer) { clearInterval(animTimer); animTimer = null; }
      if (s.type === 'chart-line') {
        const face = cube.querySelector('.face'); // front face is first child after render
        const div = face.querySelector('[id^="chart-line-"]');
        if (div) drawLineChart(div);
      } else if (s.type === 'chart-bar') {
        const face = cube.querySelector('.face');
        const div = face.querySelector('[id^="chart-bar-"]');
        if (div) drawBarChart(div);
      }
    }

    function drawLineChart(container) {
      const n = 30;
      const x = Array.from({length: n}, (_, i) => i + 1);
      let y = Array.from({length: n}, () => 50 + Math.random() * 20);
      const data = [{
        x, y, mode: 'lines+markers', name: 'Serie',
        line: { width: 3 },
        marker: { size: 6 }
      }];
      const layout = {
        margin: { l: 40, r: 20, t: 10, b: 30 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#eaeaea' },
        xaxis: { gridcolor: 'rgba(255,255,255,0.08)' },
        yaxis: { gridcolor: 'rgba(255,255,255,0.08)' },
        hovermode: 'x unified',
        transition: { duration: 300 }
      };
      Plotly.newPlot(container, data, layout, {displayModeBar: false});

      const onEnter = () => {
        if (animTimer) return;
        animTimer = setInterval(() => {
          // light random walk animation
          y = y.map((v) => v + (Math.random() - 0.5) * 1.2);
          Plotly.update(container, { y: [y] }, {}, [0]);
        }, 350);
      };
      const onLeave = () => { if (animTimer) { clearInterval(animTimer); animTimer = null; } };

      container.addEventListener('mouseenter', onEnter);
      container.addEventListener('mouseleave', onLeave);
    }

    function drawBarChart(container) {
      const cats = ['Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8'];
      let y = cats.map(() => 10 + Math.round(Math.random() * 30));
      const data = [{
        x: cats, y, type: 'bar', name: 'Valores',
      }];
      const layout = {
        margin: { l: 40, r: 20, t: 10, b: 40 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#eaeaea' },
        xaxis: { gridcolor: 'rgba(255,255,255,0.08)' },
        yaxis: { gridcolor: 'rgba(255,255,255,0.08)' },
        transition: { duration: 300 }
      };
      Plotly.newPlot(container, data, layout, {displayModeBar: false});

      const onEnter = () => {
        if (animTimer) return;
        animTimer = setInterval(() => {
          // jitter animation on hover
          const y2 = y.map((v) => v + (Math.random() - 0.5) * 2.0);
          Plotly.update(container, { y: [y2] }, {}, [0]);
        }, 300);
      };
      const onLeave = () => { if (animTimer) { clearInterval(animTimer); animTimer = null; } };
      container.addEventListener('mouseenter', onEnter);
      container.addEventListener('mouseleave', onLeave);
    }

    // Initialize
    function init() {
      ensureFaces();
      buildDots();
      render();
    }
    init();
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(TEMPLATE, slides_json=json.dumps(slides))

if __name__ == "__main__":
    # Ensure a static folder exists for future local assets
    os.makedirs("static", exist_ok=True)
    print("Presentación 3D corriendo en http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
