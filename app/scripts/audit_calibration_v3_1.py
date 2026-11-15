from argparse import ArgumentParser
from pathlib import Path

from performance_decision_engine.infrastructure.calibration_audit_v3_1 import CalibrationAuditV31


def main() -> None:
    parser = ArgumentParser(description="Audit v3 calibration without changing the frozen model or official test.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--selection-report", type=Path, required=True)
    parser.add_argument("--governance-addendum", type=Path, required=True)
    parser.add_argument("--final-model", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=1000)
    args = parser.parse_args()
    report = CalibrationAuditV31().run(
        args.source, args.protocol, args.assignments, args.selection_report,
        args.governance_addendum, args.final_model, args.output_dir, args.bootstrap
    )
    check = report["invariance_check"]
    print(f"Status: {report['status']}")
    print(f"Same-sample leakage found: {report['original_design']['same_sample_leakage_found']}")
    print(f"Raw dev ROC-AUC: {check['raw_roc_auc']:.4f}")
    print(f"Isotonic dev ROC-AUC: {check['isotonic_roc_auc']:.4f}")
    print(f"Order inversions: {check['order_inversions']}")
    print(f"New tied pairs: {check['new_tied_pairs']}")
    print(f"Official v3 changed: {report['official_v3_changed']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()

