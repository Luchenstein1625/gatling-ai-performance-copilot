param(
    [string]$RepositoryRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path $RepositoryRoot).Path

if ((Split-Path -Leaf $repoRoot) -eq "app") {
    $repoRoot = Split-Path -Parent $repoRoot
}

$mainPath = Join-Path $repoRoot "app\src\performance_decision_engine\interfaces\cli\main.py"
$developmentIndex = Join-Path $repoRoot "app\docs\development\README.md"

if (-not (Test-Path $mainPath)) {
    throw "No se encontró main.py. Ejecuta este script desde la raíz del repositorio o desde app."
}

Write-Step "Copiando archivos H10"
$relativeFiles = @(
    "app\src\performance_decision_engine\application\use_cases\run_pipeline.py",
    "app\src\performance_decision_engine\infrastructure\reporting\__init__.py",
    "app\src\performance_decision_engine\infrastructure\reporting\html_report_generator.py",
    "app\src\performance_decision_engine\interfaces\cli\pipeline.py",
    "app\tests\test_run_pipeline.py",
    "app\tests\test_html_report_generator.py",
    "app\docs\development\H10_Integration.md"
)

foreach ($relative in $relativeFiles) {
    $source = Join-Path $packageRoot $relative
    $target = Join-Path $repoRoot $relative
    $targetDirectory = Split-Path -Parent $target
    New-Item -ItemType Directory -Path $targetDirectory -Force | Out-Null
    Copy-Item $source $target -Force
}

Write-Step "Registrando pde pipeline en main.py"
$content = Get-Content $mainPath -Raw -Encoding UTF8

$importLine = "from performance_decision_engine.interfaces.cli.pipeline import register_pipeline_command"
$registerLine = "register_pipeline_command(app, console)"

if (-not $content.Contains($importLine)) {
    $importMarker = "from performance_decision_engine.infrastructure.repositories.json_execution_repository import ("
    $position = $content.IndexOf($importMarker)
    if ($position -lt 0) {
        throw "No se encontró el bloque de imports esperado en main.py."
    }
    $content = $content.Insert($position, $importLine + [Environment]::NewLine)
}

if (-not $content.Contains($registerLine)) {
    $consoleMarker = "console = Console()"
    $replacement = $consoleMarker + [Environment]::NewLine + [Environment]::NewLine + $registerLine
    if (-not $content.Contains($consoleMarker)) {
        throw "No se encontró console = Console() en main.py."
    }
    $content = $content.Replace($consoleMarker, $replacement)
}

Set-Content -Path $mainPath -Value $content -Encoding UTF8

if (Test-Path $developmentIndex) {
    Write-Step "Actualizando estado documental H10"
    $docs = Get-Content $developmentIndex -Raw -Encoding UTF8
    $docs = $docs.Replace("| H10 | Integration | ⏳ |", "| H10 | Local Integration PoC | ✅ |")
    $docs = $docs.Replace("| H10 Integration | ⏳ |", "| H10 Local Integration PoC | ✅ |")
    Set-Content -Path $developmentIndex -Value $docs -Encoding UTF8
}

Write-Step "Reinstalando paquete editable"
Push-Location (Join-Path $repoRoot "app")
try {
    python -m pip install -e ".[dev]"
    if ($LASTEXITCODE -ne 0) {
        throw "Falló la instalación editable."
    }

    Write-Step "Verificando registro del comando"
    $help = pde --help | Out-String
    if ($help -notmatch "(?m)^\s*pipeline\s") {
        Write-Host $help
        throw "El comando pipeline no aparece en pde --help."
    }

    Write-Host ""
    Write-Host "H10 instalado correctamente." -ForegroundColor Green
    Write-Host "El comando pde pipeline ya está disponible." -ForegroundColor Green
    Write-Host ""
    pde pipeline --help
}
finally {
    Pop-Location
}
