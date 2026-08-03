param(
    [Parameter(Mandatory = $true)]
    [string]$Dataset,

    [Parameter(Mandatory = $true)]
    [string]$Performance,

    [Parameter(Mandatory = $true)]
    [string]$Parameters,

    [Parameter(Mandatory = $true)]
    [string]$Results,

    [string]$Assertions,
    [string]$ComponentId,
    [string]$EvolutionHistory,
    [int]$CurrentQuadrant = 5,
    [string]$OutputDirectory = ".\examples\output\august_poc"
)

$ErrorActionPreference = "Stop"

foreach ($requiredPath in @($Dataset, $Performance, $Parameters, $Results)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required file does not exist: $requiredPath"
    }
}

if ($Assertions -and -not (Test-Path -LiteralPath $Assertions -PathType Leaf)) {
    throw "Assertions file does not exist: $Assertions"
}

if ([bool]$ComponentId -xor [bool]$EvolutionHistory) {
    throw "ComponentId and EvolutionHistory must be provided together."
}

if ($EvolutionHistory -and -not (Test-Path -LiteralPath $EvolutionHistory -PathType Leaf)) {
    throw "Evolution history file does not exist: $EvolutionHistory"
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$modelPath = Join-Path $OutputDirectory "decision_tree.joblib"
$trainingReport = Join-Path $OutputDirectory "training_report.json"
$qualityReport = Join-Path $OutputDirectory "dataset_quality.json"
$evaluationReport = Join-Path $OutputDirectory "model_comparison.json"
$explanation = Join-Path $OutputDirectory "model_explanation.json"
$prediction = Join-Path $OutputDirectory "prediction.json"
$recommendation = Join-Path $OutputDirectory "recommendation.json"
$evaluatedRecommendation = Join-Path $OutputDirectory "evolution_recommendation.json"
$quadrantPlan = Join-Path $OutputDirectory "quadrant_action.json"

pde data-quality --dataset $Dataset --output $qualityReport
pde evaluate-model --dataset $Dataset --output $evaluationReport --seeds 10
pde train-model --dataset $Dataset --model $modelPath --report $trainingReport
pde explain-model --model $modelPath --output $explanation

$commonArguments = @(
    "--performance", $Performance,
    "--parameters", $Parameters,
    "--results", $Results
)
if ($Assertions) {
    $commonArguments += @("--assertions", $Assertions)
}

& pde recommend @commonArguments --output $recommendation
& pde predict --model $modelPath @commonArguments --output $prediction

$recommendationForPlan = $recommendation
if ($ComponentId -and $EvolutionHistory) {
    pde evaluate-evolution `
        --recommendation $recommendation `
        --history $EvolutionHistory `
        --component-id $ComponentId `
        --output $evaluatedRecommendation
    $recommendationForPlan = $evaluatedRecommendation
}

pde plan-quadrant `
    --recommendation $recommendationForPlan `
    --current-quadrant $CurrentQuadrant `
    --output $quadrantPlan

Write-Host ""
Write-Host "August PoC evidence generated in: $OutputDirectory" -ForegroundColor Green
Get-ChildItem -LiteralPath $OutputDirectory -File |
    Select-Object Name, Length |
    Format-Table -AutoSize
