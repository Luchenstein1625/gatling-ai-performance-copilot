import argparse
import json
from pathlib import Path

from performance_decision_engine.infrastructure.configuration_training_v2 import (
    ConfigurationTrainingV2,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train the leakage-resistant configuration-only v2 experiment."
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = ConfigurationTrainingV2().run(args.source, args.output_dir)
    print(f"Training rows: {report['training_rows']}")
    print(f"Selected model: {report['selected_model']}")
    print(f"OOF-selected threshold: {report['selected_threshold']}")
    print(f"Created: {args.output_dir}")
    print(json.dumps(report["split"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
