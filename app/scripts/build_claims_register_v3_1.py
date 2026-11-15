from argparse import ArgumentParser
import csv
import json
from pathlib import Path

from performance_decision_engine.infrastructure.claims_v3_1 import build_claims_register


def main() -> None:
    parser = ArgumentParser(description="Build the v3.1 evidence and claims register from frozen artifacts.")
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.results_root
    rows, summary = build_claims_register(
        root / "final_test_v3/final_test_evaluation_v3.json",
        root / "final_test_v3/final_test_grouped_bootstrap_v3.csv",
        root / "fine_threshold_v3/fine_threshold_decision_v3.json",
        root / "recommender_v3/recommender_v3.json",
        root / "economics_v3/economic_evaluation_v3.json",
        root / "v3_1/calibration_audit/audit_findings.json",
        root / "v3_1/recommender_audit/recommender_audit_v3_1.json",
        root / "v3_1/recommender_confounding/recommender_confounding_audit_v3_1.json",
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "claims_register_v3_1.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output_dir / "claims_summary_v3_1.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Status: {summary['status']}")
    print(f"Registered claims: {summary['claims']}")
    print(f"Top 30% rows: {summary['top_30_rows']}")
    interval = summary["additional_cases_bootstrap"]
    print(f"Additional cases point: {summary['additional_cases_point']:.2f}")
    print(f"Additional cases grouped IC95%: [{interval['lower_95']:.2f}, {interval['upper_95']:.2f}]")
    print(f"Official v3 changed: {summary['official_v3_changed']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()

