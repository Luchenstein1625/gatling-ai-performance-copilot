from argparse import ArgumentParser
from pathlib import Path

from performance_decision_engine.infrastructure.overlap_audit_v3_1 import OverlapAuditV31


def main() -> None:
    parser = ArgumentParser(description="Audit historical Build_Id overlap with the frozen v3 test.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--governance-addendum", type=Path, required=True)
    parser.add_argument("--final-model", type=Path, required=True)
    parser.add_argument("--final-test-report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=2000)
    args = parser.parse_args()
    report = OverlapAuditV31().run(
        args.source, args.protocol, args.assignments, args.governance_addendum,
        args.final_model, args.final_test_report, args.output_dir, args.bootstrap,
    )
    print(f"Status: {report['status']}")
    print(f"Eligible builds: {report['source_builds_eligible']}")
    print(f"V3 test builds: {report['v3_test_builds']}")
    print(
        "Test builds seen in v2 fixed holdout: "
        f"{report['v3_test_builds_seen_in_v2_fixed_holdout']} "
        f"({report['v3_test_builds_seen_in_v2_fixed_holdout_pct']:.2%})"
    )
    print(f"Test builds not seen in v2 fixed holdout: {report['v3_test_builds_not_seen_in_v2_fixed_holdout']}")
    print(f"Test builds never in any v2 holdout: {report['v3_test_builds_never_in_any_v2_holdout']}")
    print(f"Official v3 changed: {report['official_v3_changed']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()

