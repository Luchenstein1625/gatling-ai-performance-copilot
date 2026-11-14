import argparse
from pathlib import Path

from performance_decision_engine.infrastructure.configuration_explainability_v2 import (
    ConfigurationExplainabilityV2,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Explain configuration-only v2 models")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--permutations", type=int, default=50)
    args = parser.parse_args()
    report = ConfigurationExplainabilityV2().run(
        args.source, args.output_dir, args.permutations
    )
    section = report["random_forest_grouped_permutation_importance"]
    print(f"Training rows: {report['training_rows']}")
    print(f"Holdout ROC-AUC: {section['baseline_roc_auc']:.4f}")
    print("Grouped permutation importance:")
    for row in section["results"]:
        print(
            f"- {row['feature']}: {row['mean']:.4f} "
            f"[{row['lower_95']:.4f}, {row['upper_95']:.4f}]"
        )
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()
