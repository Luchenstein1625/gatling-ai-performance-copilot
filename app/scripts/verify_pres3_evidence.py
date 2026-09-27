"""Verify that the committed Pres3 evidence is complete and internally consistent."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "Resultados" / "complete_feedback"
REPORT_PATH = RESULTS / "complete_pipeline_evaluation.json"

REQUIRED_ARTIFACTS = {
    "complete_pipeline_evaluation.json",
    "decision_tree.dot",
    "decision_tree_rules.txt",
    "layer1_applicability_model.joblib",
    "layered_recommendations.csv",
    "segment_metrics.csv",
    "threshold_cost_analysis.csv",
    "threshold_comparison.csv",
    "economic_sensitivity.csv",
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def main() -> None:
    missing = sorted(name for name in REQUIRED_ARTIFACTS if not (RESULTS / name).exists())
    if missing:
        fail(f"missing artifacts: {', '.join(missing)}")

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    layer1 = report["layers"]["1_applicability"]
    layer2 = report["layers"]["2_decision"]

    if report["usable_rows"] != 6444:
        fail(f"expected 6444 usable rows, found {report['usable_rows']}")
    if layer1["selected_model"] != "random_forest":
        fail(f"unexpected selected model: {layer1['selected_model']}")
    if report["layers"]["4_evaluation"]["group_overlap"] != 0:
        fail("train and holdout share Build_Id values")

    threshold = float(layer1["decision_threshold"])
    with (RESULTS / "threshold_cost_analysis.csv").open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    selected_rows = [row for row in rows if float(row["threshold"]) == threshold]
    if len(selected_rows) != 1:
        fail(f"threshold {threshold:.2f} is not uniquely represented in the cost analysis")

    selected = selected_rows[0]
    expected_distribution = layer2["holdout_distribution"]
    if int(selected["manual_reviews"]) != int(expected_distribution["review"]):
        fail("manual review count differs from the layer-2 review distribution")

    with (RESULTS / "threshold_comparison.csv").open(encoding="utf-8", newline="") as source:
        comparison = {row["scenario"]: row for row in csv.DictReader(source)}
    reference_cost = float(comparison["reference"]["total_cost_units"])
    selected_cost = float(comparison["selected"]["total_cost_units"])
    if selected_cost >= reference_cost:
        fail("selected threshold does not improve cost over the 0.50 reference")

    with (RESULTS / "economic_sensitivity.csv").open(encoding="utf-8", newline="") as source:
        economic_rows = list(csv.DictReader(source))
    base_cases = [row for row in economic_rows if row["is_base_case"] == "True"]
    if len(base_cases) != 1:
        fail("economic sensitivity must contain exactly one base case")
    if float(base_cases[0]["gross_benefit_potential_clp"]) != 12_096_000:
        fail("unexpected gross benefit potential in the economic base case")

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
    print(
        "Decision distribution: "
        f"review={expected_distribution['review']}, "
        f"maintain={expected_distribution['maintain']}, "
        f"upgrade={expected_distribution['upgrade']}"
    )


if __name__ == "__main__":
    main()
