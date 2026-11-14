import argparse
import json
from pathlib import Path

from performance_decision_engine.infrastructure.configuration_stability_v2 import (
    ConfigurationStabilityV2,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Grouped stability analysis for training v2")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--splits", type=int, default=20)
    parser.add_argument("--bootstrap", type=int, default=1000)
    args = parser.parse_args()
    report = ConfigurationStabilityV2().run(
        args.source, args.output_dir, args.splits, args.bootstrap
    )
    print(f"Training rows: {report['training_rows']}")
    print(f"Builds: {report['builds']}")
    print(f"Repeated grouped splits: {args.splits}")
    print(
        "Valid grouped bootstrap repetitions: "
        f"{report['grouped_paired_bootstrap']['valid_repetitions']}"
    )
    print(f"Created: {args.output_dir}")
    print(json.dumps(report["grouped_paired_bootstrap"]["rf_minus_logistic"], indent=2))


if __name__ == "__main__":
    main()
