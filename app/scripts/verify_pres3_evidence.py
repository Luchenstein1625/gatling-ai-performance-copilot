"""Verify that the committed Pres3 evidence is complete and internally consistent."""

from __future__ import annotations

import csv
import json
from argparse import ArgumentParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = ROOT / "Resultados" / "complete_feedback"

REQUIRED_ARTIFACTS = {
    "complete_pipeline_evaluation.json",
    "decision_tree.dot",
    "decision_tree_rules.txt",
    "layer1_applicability_model.joblib",
    "layered_recommendations.csv",
    "segment_metrics.csv",
    "threshold_cost_analysis.csv",
    "threshold_oof_analysis.csv",
    "threshold_comparison.csv",
    "paired_model_comparison.csv",
    "economic_sensitivity.csv",
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def _parse_args() -> Path:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_RESULTS,
        help="Directory created by 'pde evaluate-complete'.",
    )
    return parser.parse_args().output_dir.resolve()


def main() -> None:
    results = _parse_args()
    report_path = results / "complete_pipeline_evaluation.json"
    missing = sorted(name for name in REQUIRED_ARTIFACTS if not (results / name).exists())
    if missing:
        fail(f"missing artifacts: {', '.join(missing)}")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    layer1 = report["layers"]["1_applicability"]
    layer2 = report["layers"]["2_decision"]

    if report["usable_rows"] != 6444:
        fail(f"expected 6444 usable rows, found {report['usable_rows']}")
    if layer1["selected_model"] != "random_forest":
        fail(f"unexpected selected model: {layer1['selected_model']}")
    if report["layers"]["4_evaluation"]["group_overlap"] != 0:
        fail("train and holdout share Build_Id values")
    if layer1["threshold_selection"].get("evaluation_set") != "train_oof_groupkfold":
        fail("decision threshold was not selected from grouped OOF training predictions")
    if layer1["threshold_holdout_evaluation"].get("evaluation_set") != "untouched_holdout":
        fail("holdout threshold evaluation is missing")

    threshold = float(layer1["decision_threshold"])
    with (results / "threshold_cost_analysis.csv").open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    selected_rows = [row for row in rows if float(row["threshold"]) == threshold]
    if len(selected_rows) != 1:
        fail(f"threshold {threshold:.2f} is not uniquely represented in the cost analysis")

    selected = selected_rows[0]
    expected_distribution = layer2["holdout_distribution"]
    if int(selected["manual_reviews"]) != int(expected_distribution["review"]):
        fail("manual review count differs from the layer-2 review distribution")

    with (results / "threshold_comparison.csv").open(encoding="utf-8", newline="") as source:
        comparison = {row["scenario"]: row for row in csv.DictReader(source)}
    reference_cost = float(comparison["reference"]["total_cost_units"])
    selected_cost = float(comparison["selected"]["total_cost_units"])
    if selected_cost >= reference_cost:
        fail("selected threshold does not improve cost over the 0.50 reference")

    with (results / "economic_sensitivity.csv").open(encoding="utf-8", newline="") as source:
        economic_rows = list(csv.DictReader(source))
    base_cases = [row for row in economic_rows if row["is_base_case"] == "True"]
    if len(base_cases) != 1:
        fail("economic sensitivity must contain exactly one base case")
    if float(base_cases[0]["gross_benefit_potential_clp"]) != 12_096_000:
        fail("unexpected gross benefit potential in the economic base case")
    base_economics = report["economic_evaluation"]["base_case"]
    if float(base_economics["annual_operating_cost_clp"]) != 1_296_240:
        fail("unexpected annual operating cost")
    if float(base_economics["net_benefit_potential_clp"]) != 10_799_760:
        fail("unexpected net benefit potential")

    paired = layer1["paired_random_forest_vs_logistic_regression"]
    if paired["method"] != "paired bootstrap by Build_Id on untouched holdout":
        fail("paired RF vs logistic comparison is missing")

    with (results / "layered_recommendations.csv").open(encoding="utf-8", newline="") as source:
        recommendations = list(csv.DictReader(source))
    invalid_upgrades = [
        row
        for row in recommendations
        if row["action"] == "upgrade" and not row.get("changed_parameter")
    ]
    if invalid_upgrades:
        fail("one or more upgrade recommendations do not change a parameter")

    folds = layer1["grouped_cross_validation"]["folds"]
    if len(folds) != 5:
        fail(f"expected five grouped folds, found {len(folds)}")

    metrics = layer1["models"]["random_forest"]["test"]
    print("Pres3 evidence verified")
    print(f"Rows: {report['usable_rows']}")
    print(f"Selected model: {layer1['selected_model']}")
    print(f"Holdout accuracy: {metrics['accuracy']:.4f}")
    print(f"Holdout F1 not_applies: {metrics['not_applies_f1']:.4f}")
    print(f"Holdout recall not_applies: {metrics['not_applies_recall']:.4f}")
    print(f"Decision threshold: {threshold:.2f}")
    print(f"Threshold F1 not_applies: {float(selected['not_applies_f1']):.4f}")
    print(f"Expected cost units: {float(selected['total_cost_units']):.0f}")
    print(
        f"Cost reduction vs threshold 0.50: {(reference_cost - selected_cost) / reference_cost:.1%}"
    )
    print(
        "Gross benefit potential (base case): "
        f"CLP {float(base_cases[0]['gross_benefit_potential_clp']):,.0f}"
    )
    print(f"Annual operating cost: CLP {float(base_economics['annual_operating_cost_clp']):,.0f}")
    print(f"Net benefit potential: CLP {float(base_economics['net_benefit_potential_clp']):,.0f}")
    print(f"Projected ROI: {float(base_economics['projected_roi']):.1%}")
    print(
        "Decision distribution: "
        f"review={expected_distribution['review']}, "
        f"maintain={expected_distribution['maintain']}, "
        f"upgrade={expected_distribution['upgrade']}"
    )


if __name__ == "__main__":
    main()
