from argparse import ArgumentParser
from pathlib import Path

from performance_decision_engine.infrastructure.recommender_confounding_v3_1 import RecommenderConfoundingV31


def main() -> None:
    parser = ArgumentParser(description="Diagnose context confounding in recommender monotonicity using train+dev only.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--governance-addendum", type=Path, required=True)
    parser.add_argument("--recommender-audit", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = RecommenderConfoundingV31().run(
        args.source, args.protocol, args.assignments, args.governance_addendum,
        args.recommender_audit, args.output_dir
    )
    print(f"Status: {report['status']}")
    print(f"Test status: {report['test_status']}")
    print(f"Finding: {report['finding']}")
    print(f"Pooled weighted monotonicity: {report['pooled_weighted_monotonicity']:.2%}")
    value = report["stratified_weighted_monotonicity"]
    print(f"Stratified weighted monotonicity: {'not estimable' if value is None else f'{value:.2%}'}")
    print(f"Direction-reversal pairs: {report['direction_reversal_pairs']}")
    print(f"Context fields added to model: {report['context_fields_added_to_model']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()

