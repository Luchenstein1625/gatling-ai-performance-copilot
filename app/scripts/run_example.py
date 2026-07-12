from pathlib import Path

from performance_decision_engine.adapters.execution_builder import build_execution_summary
from performance_decision_engine.storage.json_store import save_model_json


def main() -> None:
    summary = build_execution_summary(
        performance_path=Path("examples/input/performance.yaml"),
        parameters_path=Path("examples/input/parametricConfigurationValues.yaml"),
        gatling_path=Path("examples/input/global_stats.json"),
    )
    output = Path("examples/output/execution_summary.json")
    save_model_json(summary, output)
    print(f"Created: {output}")


if __name__ == "__main__":
    main()
