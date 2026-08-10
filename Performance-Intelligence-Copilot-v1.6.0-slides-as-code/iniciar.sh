#!/usr/bin/env bash
set -euo pipefail

if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: Node.js no está instalado. Instala Node.js 22.13 o superior."
  exit 1
fi

if [ ! -d node_modules ]; then
  echo "Instalando dependencias..."
  npm install
fi

echo "Iniciando presentación..."
npm run dev
