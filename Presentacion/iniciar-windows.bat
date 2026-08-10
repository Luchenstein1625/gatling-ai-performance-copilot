@echo off
title Performance Intelligence Copilot
where node >nul 2>nul
if errorlevel 1 (
  echo ERROR: Node.js no esta instalado. Instala Node.js 22.13 o superior.
  pause
  exit /b 1
)
if not exist node_modules (
  echo Instalando dependencias...
  call npm install
  if errorlevel 1 pause & exit /b 1
)
echo Iniciando presentacion...
call npm run dev

