import argparse
from pathlib import Path

from performance_decision_engine.infrastructure.model_selection_v3 import ModelSelectionV3


def main() -> None:
    parser = argparse.ArgumentParser(description="Tune final candidates on frozen train/dev")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = ModelSelectionV3().run(
        args.source, args.protocol, args.assignments, args.output_dir
    )
    print(f"Train rows used: {report['rows']['train_used']}")
    print(f"Dev rows used: {report['rows']['dev_used']}")
    print(f"Test rows reserved: {report['rows']['test_reserved_not_evaluated']}")
    print(f"Test status: {report['test_status']}")
    print(f"Selected model: {report['selected_model']}")
    print(f"Selected parameters: {report['selected_parameters']}")
    print(f"Dev-selected threshold: {report['selected_threshold_dev_by_cost']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()
