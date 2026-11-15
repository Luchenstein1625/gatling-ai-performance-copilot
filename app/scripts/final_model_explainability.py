from argparse import ArgumentParser
from pathlib import Path

from performance_decision_engine.infrastructure.final_model_explainability_v3_1 import FinalModelExplainabilityV31


def main() -> None:
    parser = ArgumentParser(description="Explain the frozen final v3 model using dev only.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--governance-addendum", type=Path, required=True)
    parser.add_argument("--selection-report", type=Path, required=True)
    parser.add_argument("--calibration-report", type=Path, required=True)
    parser.add_argument("--final-model", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--permutations", type=int, default=50)
    parser.add_argument("--bootstrap", type=int, default=500)
    args = parser.parse_args()
    report = FinalModelExplainabilityV31().run(
        args.source, args.protocol, args.assignments, args.governance_addendum,
        args.selection_report, args.calibration_report, args.final_model,
        args.output_dir, args.permutations, args.bootstrap,
    )
    print(f"Status: {report['status']}")
    print(f"Test status: {report['test_status']}")
    print(f"Train/dev rows: {report['rows']['train']}/{report['rows']['dev']}")
    print(f"Final artifact dev ROC-AUC descriptive: {report['variants']['final_refit_train_plus_dev_on_dev_descriptive']['baseline_dev_roc_auc']:.4f}")
    print(f"Train-only replica dev ROC-AUC OOS: {report['variants']['train_only_replica_on_dev_oos']['baseline_dev_roc_auc']:.4f}")
    print(f"Official v3 changed: {report['official_v3_changed']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()

