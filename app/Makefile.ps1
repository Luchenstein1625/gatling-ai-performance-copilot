param(
    [ValidateSet("install", "test", "quality", "format", "doctor", "example", "api")]
    [string]$Task = "doctor"
)

$ErrorActionPreference = "Stop"

switch ($Task) {
    "install" {
        python -m pip install -e ".[dev]"
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
    "doctor" {
        pde doctor
    }
    "example" {
        pde normalize `
            --performance examples/input/performance.yaml `
            --parameters examples/input/parametricConfigurationValues.yaml `
            --gatling examples/input/global_stats.json `
            --output examples/output/execution_summary.json
    }
    "api" {
        uvicorn performance_decision_engine.api.main:app --reload
    }
}
