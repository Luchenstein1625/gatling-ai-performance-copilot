import argparse
from pathlib import Path

from performance_decision_engine.infrastructure.calibration_decision_v3 import CalibrationDecisionV3


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate and select final train/dev candidate")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--selection-report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=1000)
    args = parser.parse_args()
    report = CalibrationDecisionV3().run(args.source, args.protocol, args.assignments, args.selection_report, args.output_dir, args.bootstrap)
    print(f"Test status: {report['test_status']}")
    print(f"Boosting superiority: {report['paired_boosting_minus_rf_dev']['boosting_superiority_demonstrated']}")
    print(f"Selected model: {report['selected_model']}")
    print(f"Selected calibration: {report['selected_calibration']}")
    print(f"Selected dev threshold: {report['selected_threshold_dev']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()
