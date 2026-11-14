import argparse
from pathlib import Path

from performance_decision_engine.infrastructure.fine_threshold_v3 import FineThresholdV3


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the frozen candidate on a fine dev threshold grid")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--calibration-report", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=1000)
    args = parser.parse_args()
    report = FineThresholdV3().run(
        args.source,
        args.protocol,
        args.assignments,
        args.calibration_report,
        args.candidate,
        args.output_dir,
        args.bootstrap,
    )
    minimum = report["minimum_point_estimate"]
    interval = report["minimum_point_estimate_bootstrap"]
    print(f"Test status: {report['test_status']}")
    print(f"Point-estimate minimum threshold: {minimum['threshold']}")
    print(f"Point-estimate delta vs review all: {minimum['delta_vs_review_all']}")
    print(f"Grouped bootstrap delta IC95%: [{interval['lower_95']}, {interval['upper_95']}]")
    print(f"Automatic-release thresholds passing both gates: {report['automatic_release_gate']['passing_thresholds']}")
    print(f"Recommended policy: {report['recommended_policy']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()
