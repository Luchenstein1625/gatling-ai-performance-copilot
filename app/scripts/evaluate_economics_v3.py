import argparse
from pathlib import Path

from performance_decision_engine.infrastructure.economics_v3 import EconomicsV3


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate conditional economic value using frozen test evidence")
    parser.add_argument("--final-test-report", type=Path, required=True)
    parser.add_argument("--bootstrap", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--simulations", type=int, default=10_000)
    parser.add_argument("--annual-attentions", type=int, default=144)
    parser.add_argument("--budget-per-attention-clp", type=float, default=224_000)
    parser.add_argument("--monthly-cloud-usd", type=float, default=100)
    parser.add_argument("--monthly-ai-usd", type=float, default=10)
    parser.add_argument("--usd-clp", type=float, default=982)
    parser.add_argument("--imputed-development-cost-clp", type=float, default=0)
    args = parser.parse_args()
    report = EconomicsV3().run(
        args.final_test_report,
        args.bootstrap,
        args.output_dir,
        args.simulations,
        args.annual_attentions,
        args.budget_per_attention_clp,
        args.monthly_cloud_usd,
        args.monthly_ai_usd,
        args.usd_clp,
        args.imputed_development_cost_clp,
    )
    print(f"Evidence status: {report['evidence_status']}")
    print(f"Annual budget: CLP {report['budgetary_inputs']['annual_budget_clp']:,.0f}")
    print(f"Annual operating cost: CLP {report['operating_cost_inputs']['annual_operating_cost_clp']:,.0f}")
    print(f"Break-even coverage × reduction: {report['break_even']['minimum_coverage_times_effort_reduction']:.2%}")
    print(f"Additional detections per 100 (point): {report['measured_model_evidence']['additional_detections_per_100_prioritized_point']:.2f}")
    print(f"Probability net benefit > 0: {report['effort_monte_carlo']['probability_net_benefit_above_zero']:.2%}")
    for row in report["effort_scenarios"]:
        print(f"- {row['scenario']}: gross CLP {row['gross_benefit_clp']:,.0f}; net CLP {row['net_benefit_clp']:,.0f}; ROI {row['roi']:.2%}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()
