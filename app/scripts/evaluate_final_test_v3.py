import argparse
from pathlib import Path

from performance_decision_engine.infrastructure.final_test_v3 import FinalTestV3


def main() -> None:
    parser = argparse.ArgumentParser(description="Open and evaluate the frozen test exactly once")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--calibration-report", type=Path, required=True)
    parser.add_argument("--fine-threshold-report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repository", type=Path, default=Path(".."))
    parser.add_argument("--required-tag", default="model-final-v3")
    parser.add_argument("--confirm-open-test", required=True)
    parser.add_argument("--bootstrap", type=int, default=2000)
    args = parser.parse_args()
    report = FinalTestV3().run(
        args.source,
        args.protocol,
        args.assignments,
        args.calibration_report,
        args.fine_threshold_report,
        args.output_dir,
        args.repository,
        args.required_tag,
        args.confirm_open_test,
        args.bootstrap,
    )
    metrics = report["ranking_test_metrics"]
    intervals = report["ranking_grouped_bootstrap_ic95"]
    print(f"Test status: {report['test_status']}")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f} [{intervals['roc_auc']['lower_95']:.4f}, {intervals['roc_auc']['upper_95']:.4f}]")
    print(f"PR-AUC: {metrics['pr_auc']:.4f} [{intervals['pr_auc']['lower_95']:.4f}, {intervals['pr_auc']['upper_95']:.4f}]")
    print(f"Recall@30: {metrics['recall_at_30']:.4f} [{intervals['recall_at_30']['lower_95']:.4f}, {intervals['recall_at_30']['upper_95']:.4f}]")
    print(f"Precision@30: {metrics['precision_at_30']:.4f} [{intervals['precision_at_30']['lower_95']:.4f}, {intervals['precision_at_30']['upper_95']:.4f}]")
    print(f"Lift@30: {metrics['lift_at_30']:.4f} [{intervals['lift_at_30']['lower_95']:.4f}, {intervals['lift_at_30']['upper_95']:.4f}]")
    print(f"Operational policy: {report['operational_policy']['name']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()
