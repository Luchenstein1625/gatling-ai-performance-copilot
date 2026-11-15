from __future__ import annotations

import csv
import html
import json
import random
from pathlib import Path
from typing import Any

import numpy as np


RANDOM_STATE = 42
FIXED_COVERAGE = 0.25
K_VALUES = (0.5, 1.0, 2.0)


def percentile_summary(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("At least one value is required")
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "lower_95": float(np.quantile(values, 0.025)),
        "upper_95": float(np.quantile(values, 0.975)),
    }


def anchored_reduction(additional_per_100: float, k: float) -> float:
    """Translate ranking evidence to an explicit effort hypothesis, floored at no benefit."""
    return min(1.0, max(0.0, k * additional_per_100 / 100.0))


def anchored_scenario(
    annual_budget_clp: float,
    annual_cost_clp: float,
    coverage: float,
    additional_per_100: float,
    k: float,
) -> dict[str, float]:
    reduction = anchored_reduction(additional_per_100, k)
    gross = annual_budget_clp * coverage * reduction
    net = gross - annual_cost_clp
    return {
        "coverage": coverage,
        "k": k,
        "additional_detections_per_100_point": additional_per_100,
        "effort_reduction_point": reduction,
        "coverage_times_reduction_point": coverage * reduction,
        "gross_benefit_point_clp": gross,
        "annual_cost_clp": annual_cost_clp,
        "net_benefit_point_clp": net,
        "roi_point": net / annual_cost_clp if annual_cost_clp else None,
    }


def break_even_reduction(annual_cost_clp: float, annual_budget_clp: float, coverage: float) -> float:
    if coverage <= 0 or annual_budget_clp <= 0:
        raise ValueError("Coverage and annual budget must be positive")
    return annual_cost_clp / annual_budget_clp / coverage


def required_annual_records(
    annual_cost_clp: float,
    value_per_detection_clp: float,
    additional_detections_per_100_prioritized: float,
    prioritized_fraction: float = 0.30,
) -> float | None:
    incremental_rate = prioritized_fraction * max(0.0, additional_detections_per_100_prioritized) / 100.0
    if value_per_detection_clp <= 0 or incremental_rate <= 0:
        return None
    return annual_cost_clp / (value_per_detection_clp * incremental_rate)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def tornado_svg(path: Path, rows: list[dict[str, Any]], annual_cost: float) -> None:
    width, height = 1000, 520
    left, centre, right = 160, 510, 900
    values = [float(row["net_benefit_point_clp"]) for row in rows]
    extent = max(max(abs(value) for value in values), annual_cost, 1.0)
    scale = (right - centre - 40) / extent
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="45" y="40" font-family="Arial" font-size="24" font-weight="700" fill="#073b66">Economía anclada · cobertura 25% · proyección condicionada</text>',
        f'<line x1="{centre}" y1="70" x2="{centre}" y2="410" stroke="#6b7c8f" stroke-width="2"/>',
        f'<text x="{centre}" y="445" text-anchor="middle" font-family="Arial" font-size="15" fill="#4a5568">0 CLP</text>',
    ]
    for position, row in enumerate(rows):
        y = 100 + position * 105
        value = float(row["net_benefit_point_clp"])
        x = centre if value >= 0 else centre + value * scale
        bar_width = abs(value * scale)
        color = "#009e95" if value >= 0 else "#a8b5bf"
        parts.extend([
            f'<text x="45" y="{y + 28}" font-family="Arial" font-size="20" fill="#17324d">k={float(row["k"]):g}</text>',
            f'<rect x="{x:.1f}" y="{y}" width="{bar_width:.1f}" height="38" rx="6" fill="{color}"/>',
            f'<text x="{centre + value * scale + (10 if value >= 0 else -10):.1f}" y="{y + 27}" text-anchor="{"start" if value >= 0 else "end"}" font-family="Arial" font-size="17" font-weight="700" fill="#17324d">{value/1_000_000:.2f} MM</text>',
            f'<text x="760" y="{y + 65}" font-family="Arial" font-size="14" fill="#4a5568">Reducción {100*float(row["effort_reduction_point"]):.1f}%</text>',
        ])
    parts.extend([
        '<text x="45" y="490" font-family="Arial" font-size="15" fill="#4a5568">Mecanismo: detección más temprana reduce reproceso y tiempo de análisis. k es una equivalencia hipotética, no medida.</text>',
        '</svg>',
    ])
    path.write_text("\n".join(parts), encoding="utf-8")


class AnchoredEconomicsV31:
    def run(
        self,
        economics_report_path: Path,
        final_test_report_path: Path,
        bootstrap_path: Path,
        governance_addendum_path: Path,
        output_dir: Path,
        simulations: int = 10_000,
    ) -> dict[str, Any]:
        economics = json.loads(economics_report_path.read_text(encoding="utf-8"))
        final_test = json.loads(final_test_report_path.read_text(encoding="utf-8"))
        addendum = json.loads(governance_addendum_path.read_text(encoding="utf-8"))
        bootstrap = _read_csv(bootstrap_path)
        if economics.get("evidence_status") != "conditional_projection_not_realized_saving":
            raise ValueError("Original economics is not marked as conditional")
        if final_test.get("test_status") != "OPENED_ONCE_EVALUATION_COMPLETE":
            raise ValueError("Frozen independent test report is incomplete")
        a1 = next((item for item in addendum.get("registered_analyses", []) if item.get("id") == "A1"), None)
        if a1 is None or tuple(float(value) for value in a1.get("fixed_k_values", [])) != K_VALUES:
            raise ValueError("A1 fixed k values are not pre-registered")
        if not bootstrap:
            raise ValueError("Frozen grouped bootstrap is empty")

        annual_budget = float(economics["budgetary_inputs"]["annual_budget_clp"])
        annual_cost = float(economics["operating_cost_inputs"]["annual_operating_cost_clp"]) + float(
            economics["operating_cost_inputs"].get("imputed_development_cost_clp", 0.0)
        )
        ranking = final_test["ranking_test_metrics"]
        point_additional = 100 * (
            float(ranking["precision_at_30"]) - float(ranking["prevalence_not_applies"])
        )
        bootstrap_additional = []
        for row in bootstrap:
            precision = float(row["precision_at_30"])
            lift = float(row["lift_at_30"])
            prevalence = precision / lift if lift else 0.0
            bootstrap_additional.append(100 * (precision - prevalence))

        scenarios = []
        for k in K_VALUES:
            point = anchored_scenario(annual_budget, annual_cost, FIXED_COVERAGE, point_additional, k)
            reductions = [anchored_reduction(value, k) for value in bootstrap_additional]
            gross = [annual_budget * FIXED_COVERAGE * value for value in reductions]
            net = [value - annual_cost for value in gross]
            roi = [value / annual_cost for value in net]
            scenarios.append({
                "scenario": f"anchored_k_{k:g}",
                **point,
                "reduction_lower_95": float(np.quantile(reductions, 0.025)),
                "reduction_upper_95": float(np.quantile(reductions, 0.975)),
                "net_benefit_lower_95_clp": float(np.quantile(net, 0.025)),
                "net_benefit_upper_95_clp": float(np.quantile(net, 0.975)),
                "roi_lower_95": float(np.quantile(roi, 0.025)),
                "roi_upper_95": float(np.quantile(roi, 0.975)),
                "probability_net_benefit_above_zero": sum(value > 0 for value in net) / len(net),
                "status": "conditional_projection_anchored_to_test_uncertainty",
            })

        break_even_product = annual_cost / annual_budget
        break_even_rows = [
            {
                "coverage": coverage,
                "minimum_effort_reduction": break_even_reduction(annual_cost, annual_budget, coverage),
                "minimum_effort_reduction_pct": 100 * break_even_reduction(annual_cost, annual_budget, coverage),
                "coverage_times_reduction_required": break_even_product,
                "annual_budget_clp": annual_budget,
                "annual_cost_clp": annual_cost,
            }
            for coverage in (0.10, 0.25, 0.50, 0.75, 1.0)
        ]

        value_rows: list[dict[str, Any]] = []
        for value in (112_000.0, 224_000.0, 448_000.0, 896_000.0):
            value_rows.append({
                "row_type": "required_annual_records_for_assumed_value",
                "annual_records_assumption": "",
                "value_per_additional_detection_clp": value,
                "required_annual_records_point": required_annual_records(
                    annual_cost, value, point_additional, 0.30
                ),
                "prioritized_fraction": 0.30,
                "additional_detections_per_100_prioritized_point": point_additional,
                "note": "Requires measured annual eligible-record volume from BCI.",
            })
        for records in (100, 250, 500, 1000):
            incremental = records * 0.30 * max(0.0, point_additional) / 100.0
            value_rows.append({
                "row_type": "minimum_value_per_detection_for_annual_records",
                "annual_records_assumption": records,
                "value_per_additional_detection_clp": annual_cost / incremental if incremental else None,
                "required_annual_records_point": records,
                "prioritized_fraction": 0.30,
                "additional_detections_per_100_prioritized_point": point_additional,
                "note": "Illustrative volume; replace with measured BCI annual eligible records.",
            })

        generator = random.Random(RANDOM_STATE)
        conditioned_rows = []
        for iteration in range(1, simulations + 1):
            coverage = generator.triangular(0.10, 0.50, 0.25)
            k = generator.triangular(0.5, 2.0, 1.0)
            additional = generator.choice(bootstrap_additional)
            reduction = anchored_reduction(additional, k)
            gross = annual_budget * coverage * reduction
            net = gross - annual_cost
            conditioned_rows.append({
                "iteration": iteration,
                "coverage": coverage,
                "k": k,
                "additional_detections_per_100_prioritized": additional,
                "effort_reduction": reduction,
                "gross_benefit_clp": gross,
                "net_benefit_clp": net,
                "roi": net / annual_cost,
            })
        net_values = [float(row["net_benefit_clp"]) for row in conditioned_rows]
        roi_values = [float(row["roi"]) for row in conditioned_rows]
        reduction_values = [float(row["effort_reduction"]) for row in conditioned_rows]
        conditioned = {
            "schema_version": "3.1",
            "status": "CONDITIONED_MONTE_CARLO_NOT_REALIZED_SAVING",
            "simulations": simulations,
            "coverage_distribution": "triangular(min=0.10, mode=0.25, max=0.50)",
            "k_distribution": "triangular(min=0.5, mode=1.0, max=2.0)",
            "additional_detection_distribution": "frozen grouped test bootstrap",
            "benefit_floor": 0.0,
            "effort_reduction": percentile_summary(reduction_values),
            "net_benefit_clp": percentile_summary(net_values),
            "roi": percentile_summary(roi_values),
            "probability_net_benefit_above_zero": sum(value > 0 for value in net_values) / simulations,
            "interpretation": "Conditioned projection; probability is driven by explicit assumptions and is not an observed saving.",
        }

        report = {
            "schema_version": "3.1",
            "alert": "A1",
            "status": "ANCHORED_ECONOMICS_COMPLETE",
            "mechanism": "Earlier detection of not_applies cases may reduce rework and QA analysis time.",
            "evidence": {
                "additional_detections_per_100_prioritized_point": point_additional,
                "additional_detections_grouped_bootstrap": percentile_summary(bootstrap_additional),
            },
            "annual_budget_clp": annual_budget,
            "annual_cost_clp": annual_cost,
            "break_even_coverage_times_reduction": break_even_product,
            "fixed_coverage_for_anchored_scenarios": FIXED_COVERAGE,
            "fixed_k_values": list(K_VALUES),
            "annual_eligible_records_status": "REQUIRES_BCI_MEASUREMENT",
            "official_v3_changed": False,
            "allowed_claim": "The projection exceeds break-even only under the stated coverage, k and effort-equivalence assumptions.",
            "prohibited_claim": "The project has already produced savings or a realized ROI.",
        }

        output_dir.mkdir(parents=True, exist_ok=True)
        _write_csv(output_dir / "anchored_scenarios.csv", scenarios)
        _write_csv(output_dir / "break_even_table.csv", break_even_rows)
        _write_csv(output_dir / "value_per_detection_table.csv", value_rows)
        _write_csv(output_dir / "conditioned_monte_carlo_draws.csv", conditioned_rows)
        tornado_svg(output_dir / "tornado.svg", scenarios, annual_cost)
        (output_dir / "monte_carlo_conditioned.json").write_text(
            json.dumps(conditioned, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (output_dir / "economics_anchored_v3_1.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report

