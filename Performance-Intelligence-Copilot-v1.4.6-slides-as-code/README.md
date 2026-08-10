# Performance Intelligence Copilot v1.4.6 — Slides as Code

Presentación web del Capstone, construida con React, TypeScript y CSS. Incluye 14 láminas, navegación por teclado, vista general, speech y exportación a PDF.

## Requisitos

- Node.js 22.13 o superior.
- npm 10 o superior.

## Levantar localmente

### Windows

Puedes hacer doble clic en `iniciar-windows.bat` o ejecutar:

```powershell
npm install
npm run dev
```

### macOS o Linux

```bash
chmod +x iniciar.sh
./iniciar.sh
```

Luego abre la URL indicada en la consola, normalmente `http://localhost:5173`.

## Navegación

- `→`, `Espacio` o `Page Down`: siguiente lámina.
- `←` o `Page Up`: lámina anterior.
- `O`: abrir o cerrar la vista general.
- `Esc`: cerrar la vista general.

## Archivos principales

- `app/page.tsx`: contenido y estructura de las 14 láminas.
- `app/globals.css`: diseño, tipografía, colores y composición.
- `presentation.config.ts`: versión y metadatos.
- `README-SPEECH.md`: speech de la exposición.
- `public/Performance-Intelligence-Copilot-v1.4.6.pdf`: PDF de la presentación.
- `scripts/export-pdf.mjs`: generación del PDF desde la presentación local.

## Validar el proyecto

```bash
npm test
```

## Exportar nuevamente a PDF

Con la presentación local ejecutándose en otra consola:

```bash
npm run export:pdf
```

## Editar las láminas

1. Modifica `app/page.tsx` para cambiar contenidos o gráficos.
2. Modifica `app/globals.css` para ajustar el diseño.
3. Actualiza `presentation.config.ts` si crearás una nueva versión.
4. Ejecuta `npm test` antes de compartirla.

