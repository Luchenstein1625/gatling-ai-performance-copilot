from argparse import ArgumentParser
from pathlib import Path

from performance_decision_engine.infrastructure.recommender_audit_v3_1 import RecommenderAuditV31


def main() -> None:
    parser = ArgumentParser(description="Audit recommender ordering, monotonicity and action stability.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--governance-addendum", type=Path, required=True)
    parser.add_argument("--recommender-report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=2000)
    args = parser.parse_args()
    report = RecommenderAuditV31().run(
        args.source, args.protocol, args.assignments, args.governance_addendum,
        args.recommender_report, args.output_dir, args.bootstrap
    )
    print(f"Status: {report['status']}")
    print(f"Test status: {report['test_status']}")
    print(f"Order encoding correct: {report['order_encoding_correct']}")
    print(f"Correction required: {report['correction_required']}")
    print(f"Monotonicity: {report['monotonicity']['consistency_rate']:.2%}")
    print(f"Weighted monotonicity: {report['monotonicity']['weighted_consistency_rate']:.2%}")
    print(f"Publishable upgrades: {report['publishable_upgrades']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()

