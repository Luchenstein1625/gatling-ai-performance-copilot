from __future__ import annotations

import argparse
from pathlib import Path

from performance_decision_engine.infrastructure.baselines_v3_1 import BaselinesV31


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate pre-registered B0 and B3 baselines on frozen train+dev only")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--governance-addendum", type=Path, required=True)
    parser.add_argument("--baseline-protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--random-repetitions", type=int, default=2000)
    args = parser.parse_args()
    report = BaselinesV31().run(
        source_path=args.source,
        protocol_path=args.protocol,
        assignments_path=args.assignments,
        governance_addendum_path=args.governance_addendum,
        baseline_protocol_path=args.baseline_protocol,
        output_dir=args.output_dir,
        bootstrap_repetitions=args.bootstrap,
        random_repetitions=args.random_repetitions,
    )
    print(f"Status: {report['status']}")
    print(f"Population: {report['population']['rows']} rows / {report['population']['builds']} builds")
    print(f"B0 Recall@30 mean: {report['B0']['recall_at_30']['mean']:.4f}")
    print(f"B3 ROC-AUC: {report['B3']['point']['roc_auc']:.4f}")
    print(f"B3 Recall@30: {report['B3']['point']['recall_at_30']:.4f}")
    print(f"Test status: {report['test_status']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()
