param(
    [ValidateSet("install", "doctor", "test", "quality", "format", "example", "api")]
    [string]$Task = "doctor"
)

$ErrorActionPreference = "Stop"

switch ($Task) {
    "install" {
        python -m pip install -e ".[dev]"
    }
    "doctor" {
        pde doctor
    }
    "test" {
        pytest
    }
    "quality" {
        ruff check .
        black --check .
        mypy src
    }
    "format" {
        black .
        ruff check . --fix
    }
    "example" {
        pde normalize `
          --performance examples/input/performance.yaml `
          --parameters examples/input/parametricConfigurationValues.yaml `
          --results examples/input/global_stats.json `
          --output examples/output/execution_summary.json
    }
    "api" {
        uvicorn performance_decision_engine.interfaces.api.main:app --reload
    }
}
