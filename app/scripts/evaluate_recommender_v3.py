import argparse
from pathlib import Path

from performance_decision_engine.infrastructure.recommender_v3 import RecommenderV3


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and backtest the train+dev configuration recommender")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=500)
    args = parser.parse_args()
    report = RecommenderV3().run(
        args.source,
        args.protocol,
        args.assignments,
        args.output_dir,
        args.bootstrap,
    )
    print(f"Test status: {report['test_status']}")
    print(f"Development rows/builds: {report['rows']}/{report['builds']}")
    print(f"Configuration cells: {report['cells']}")
    print(f"Selected rules: {report['selected_rules']}")
    print(f"Estimated actions: {report['action_distribution_estimated']}")
    print(f"Published actions: {report['action_distribution_published']}")
    print(f"Non-abstain cell coverage: {report['coverage_non_abstain_cells']:.2%}")
    print(f"Stable cells: {report['stability']['cells_agreement_at_least_80_percent']}/{report['stability']['cells_total']}")
    print(f"Monotonicity: {report['monotonicity']}")
    print(f"Publishable upgrades: {report['publishable_upgrades']}")
    print(f"Gate status: {report['gate_status']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()
