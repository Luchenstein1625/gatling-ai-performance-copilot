from argparse import ArgumentParser
from pathlib import Path

from performance_decision_engine.infrastructure.economics_anchored_v3_1 import AnchoredEconomicsV31


def main() -> None:
    parser = ArgumentParser(description="Build evidence-anchored conditional economics v3.1.")
    parser.add_argument("--economics-report", type=Path, required=True)
    parser.add_argument("--final-test-report", type=Path, required=True)
    parser.add_argument("--bootstrap", type=Path, required=True)
    parser.add_argument("--governance-addendum", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--simulations", type=int, default=10_000)
    args = parser.parse_args()
    report = AnchoredEconomicsV31().run(
        args.economics_report, args.final_test_report, args.bootstrap,
        args.governance_addendum, args.output_dir, args.simulations,
    )
    evidence = report["evidence"]["additional_detections_grouped_bootstrap"]
    print(f"Status: {report['status']}")
    print(f"Mechanism: {report['mechanism']}")
    print(f"Additional detections per 100 point: {report['evidence']['additional_detections_per_100_prioritized_point']:.2f}")
    print(f"Additional detections IC95%: [{evidence['lower_95']:.2f}, {evidence['upper_95']:.2f}]")
    print(f"Break-even coverage x reduction: {report['break_even_coverage_times_reduction']:.2%}")
    print(f"Annual eligible records: {report['annual_eligible_records_status']}")
    print(f"Official v3 changed: {report['official_v3_changed']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()

