from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from performance_decision_engine.infrastructure.release_audit_v3_1 import ReleaseAuditV31


def main() -> None:
    parser = ArgumentParser(description="Integrate and verify release v3.1 without retraining or reopening test")
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-test-suite", action="store_true")
    args = parser.parse_args()
    result = ReleaseAuditV31().run(
        args.repository,
        args.results_root,
        args.source,
        args.output_dir,
        run_test_suite=args.run_test_suite,
    )
    check = result["reproducibility"]
    metrics = result["official_metrics"]["independent_test"]
    print(f"Release status: {check['release_status']}")
    print(f"Checks: {check['checks_passed']} passed; {check['checks_failed']} failed")
    print(f"Official test: {metrics['rows']} rows / {metrics['builds']} builds")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    print(f"Recall@30: {metrics['recall_at_30']:.4f}")
    print(f"Operational policy: {result['official_metrics']['operational_policy']['name']}")
    print(f"Created: {args.output_dir}")
    if check["release_status"] == "BLOCKED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
