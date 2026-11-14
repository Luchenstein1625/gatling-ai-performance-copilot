"""Reproducible economic scenarios using the frozen independent-test evidence."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

import numpy as np

RANDOM_STATE = 42


def annual_operating_cost(
    monthly_cloud_usd: float, monthly_ai_usd: float, usd_clp: float
) -> float:
    return (monthly_cloud_usd + monthly_ai_usd) * 12 * usd_clp


def effort_scenario(
    name: str,
    annual_budget_clp: float,
    coverage: float,
    effort_reduction: float,
    operating_cost_clp: float,
    imputed_development_cost_clp: float = 0.0,
) -> dict[str, object]:
    gross = annual_budget_clp * coverage * effort_reduction
    total_cost = operating_cost_clp + imputed_development_cost_clp
    net = gross - total_cost
    return {
        "scenario": name,
        "annual_budget_clp": annual_budget_clp,
        "coverage_assumption": coverage,
        "effort_reduction_assumption": effort_reduction,
        "coverage_times_reduction": coverage * effort_reduction,
        "gross_benefit_clp": gross,
        "annual_operating_cost_clp": operating_cost_clp,
        "imputed_development_cost_clp": imputed_development_cost_clp,
        "total_cost_clp": total_cost,
        "net_benefit_clp": net,
        "roi": net / total_cost if total_cost else None,
        "payback_months": 12 * total_cost / gross if gross > 0 else None,
        "status": "conditional_projection_not_realized_saving",
    }


def additional_detections_per_100(precision_at_30: float, prevalence: float) -> float:
    return 100 * (precision_at_30 - prevalence)


def percentile_summary(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("At least one value is required")
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "lower_95": float(np.quantile(values, 0.025)),
        "upper_95": float(np.quantile(values, 0.975)),
    }


class EconomicsV3:
    @staticmethod
    def _read_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8", newline="") as source:
            return list(csv.DictReader(source))

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _summary_svg(path: Path, scenarios: list[dict[str, object]], operating_cost: float) -> None:
        width, height = 980, 500
        left, top, bottom = 100, 70, 100
        chart_height = height - top - bottom
        values = [float(row["gross_benefit_clp"]) for row in scenarios]
        maximum = max(values + [operating_cost]) * 1.15
        bar_width = 120
        positions = [190, 430, 670]

        def y(value: float) -> float:
            return top + chart_height * (1 - value / maximum)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="white"/>',
            '<style>text{font-family:Arial;fill:#263746}.title{font-size:20px;font-weight:bold}.label{font-size:14px}.value{font-size:14px;font-weight:bold}</style>',
            '<text x="100" y="32" class="title">Proyección económica condicionada · no es ahorro realizado</text>',
            f'<line x1="{left}" y1="{top+chart_height}" x2="900" y2="{top+chart_height}" stroke="#7c8993"/>',
            f'<line x1="{left}" y1="{y(operating_cost):.1f}" x2="900" y2="{y(operating_cost):.1f}" stroke="#d1495b" stroke-width="2" stroke-dasharray="7 6"/>',
            f'<text x="705" y="{y(operating_cost)-8:.1f}" class="label">Operación CLP {operating_cost/1_000_000:.2f} MM</text>',
        ]
        for x, row in zip(positions, scenarios, strict=True):
            gross = float(row["gross_benefit_clp"])
            net = float(row["net_benefit_clp"])
            height_bar = top + chart_height - y(gross)
            color = "#009b8c" if net >= 0 else "#a8b5bf"
            parts.extend([
                f'<rect x="{x}" y="{y(gross):.1f}" width="{bar_width}" height="{height_bar:.1f}" rx="8" fill="{color}"/>',
                f'<text x="{x+bar_width/2}" y="{y(gross)-10:.1f}" text-anchor="middle" class="value">{gross/1_000_000:.2f} MM</text>',
                f'<text x="{x+bar_width/2}" y="{top+chart_height+28}" text-anchor="middle" class="label">{row["scenario"]}</text>',
                f'<text x="{x+bar_width/2}" y="{top+chart_height+50}" text-anchor="middle" class="label">Neto {net/1_000_000:.2f} MM</text>',
            ])
        parts.extend([
            '<text x="100" y="475" class="label">Beneficio bruto = presupuesto anual × cobertura × reducción de esfuerzo. Todos los porcentajes son supuestos a validar.</text>',
            '</svg>',
        ])
        path.write_text("\n".join(parts), encoding="utf-8")

    def run(
        self,
        final_test_report_path: Path,
        bootstrap_path: Path,
        output_dir: Path,
        simulations: int = 10_000,
        annual_attentions: int = 144,
        budget_per_attention_clp: float = 224_000,
        monthly_cloud_usd: float = 100,
        monthly_ai_usd: float = 10,
        usd_clp: float = 982,
        imputed_development_cost_clp: float = 0,
    ) -> dict[str, object]:
        report = json.loads(final_test_report_path.read_text(encoding="utf-8"))
        if report["test_status"] != "OPENED_ONCE_EVALUATION_COMPLETE":
            raise ValueError("Final independent test report is not complete")
        bootstrap = self._read_csv(bootstrap_path)
        if not bootstrap:
            raise ValueError("Grouped test bootstrap is empty")

        annual_budget = annual_attentions * budget_per_attention_clp
        operating_cost = annual_operating_cost(monthly_cloud_usd, monthly_ai_usd, usd_clp)
        assumptions = [
            ("conservative", 0.10, 0.25),
            ("base", 0.25, 0.50),
            ("optimistic", 0.50, 0.75),
        ]
        scenarios = [
            effort_scenario(
                name,
                annual_budget,
                coverage,
                reduction,
                operating_cost,
                imputed_development_cost_clp,
            )
            for name, coverage, reduction in assumptions
        ]

        sensitivity = [
            effort_scenario(
                f"coverage_{coverage:.2f}_reduction_{reduction:.2f}",
                annual_budget,
                coverage,
                reduction,
                operating_cost,
                imputed_development_cost_clp,
            )
            for coverage in (0.10, 0.25, 0.50)
            for reduction in (0.25, 0.50, 0.75)
        ]

        ranking = report["ranking_test_metrics"]
        point_prevalence = float(ranking["prevalence_not_applies"])
        point_precision = float(ranking["precision_at_30"])
        point_additional = additional_detections_per_100(point_precision, point_prevalence)
        bootstrap_additional: list[float] = []
        for row in bootstrap:
            precision = float(row["precision_at_30"])
            lift = float(row["lift_at_30"])
            prevalence = precision / lift if lift else 0.0
            bootstrap_additional.append(additional_detections_per_100(precision, prevalence))
        additional_summary = percentile_summary(bootstrap_additional)

        generator = random.Random(RANDOM_STATE)
        monte_carlo: list[dict[str, object]] = []
        for iteration in range(1, simulations + 1):
            coverage = generator.triangular(0.10, 0.50, 0.25)
            reduction = generator.triangular(0.25, 0.75, 0.50)
            gross = annual_budget * coverage * reduction
            total_cost = operating_cost + imputed_development_cost_clp
            net = gross - total_cost
            additional = generator.choice(bootstrap_additional)
            value_per_early_detection = generator.triangular(
                budget_per_attention_clp * 0.5,
                budget_per_attention_clp * 4.0,
                budget_per_attention_clp,
            )
            normalized_detection_value = additional * value_per_early_detection
            monte_carlo.append({
                "iteration": iteration,
                "coverage": coverage,
                "effort_reduction": reduction,
                "coverage_times_reduction": coverage * reduction,
                "gross_benefit_clp": gross,
                "total_cost_clp": total_cost,
                "net_benefit_clp": net,
                "roi": net / total_cost if total_cost else None,
                "additional_detections_per_100_prioritized": additional,
                "assumed_value_per_early_detection_clp": value_per_early_detection,
                "normalized_detection_value_per_100_prioritized_clp": normalized_detection_value,
            })

        net_values = [float(row["net_benefit_clp"]) for row in monte_carlo]
        roi_values = [float(row["roi"]) for row in monte_carlo]
        gross_values = [float(row["gross_benefit_clp"]) for row in monte_carlo]
        detection_values = [
            float(row["normalized_detection_value_per_100_prioritized_clp"])
            for row in monte_carlo
        ]
        break_even_product = (
            operating_cost + imputed_development_cost_clp
        ) / annual_budget
        break_even = [
            {
                "coverage": coverage,
                "minimum_effort_reduction": break_even_product / coverage,
                "coverage_times_reduction_required": break_even_product,
                "annual_budget_clp": annual_budget,
                "total_cost_clp": operating_cost + imputed_development_cost_clp,
            }
            for coverage in (0.10, 0.25, 0.50, 0.75, 1.0)
        ]

        output_dir.mkdir(parents=True, exist_ok=True)
        self._write_csv(output_dir / "economic_scenarios_v3.csv", scenarios)
        self._write_csv(output_dir / "economic_sensitivity_v3.csv", sensitivity)
        self._write_csv(output_dir / "economic_monte_carlo_v3.csv", monte_carlo)
        self._write_csv(output_dir / "break_even_v3.csv", break_even)
        self._summary_svg(output_dir / "economic_summary_v3.svg", scenarios, operating_cost)

        evaluation: dict[str, object] = {
            "schema_version": "3.0",
            "experiment": "economic_evaluation_using_frozen_test_uncertainty",
            "evidence_status": "conditional_projection_not_realized_saving",
            "measured_model_evidence": {
                "source": str(final_test_report_path),
                "roc_auc": ranking["roc_auc"],
                "precision_at_30": point_precision,
                "prevalence_not_applies": point_prevalence,
                "additional_detections_per_100_prioritized_point": point_additional,
                "additional_detections_per_100_prioritized_bootstrap": additional_summary,
            },
            "budgetary_inputs": {
                "annual_attentions": annual_attentions,
                "budget_per_attention_clp": budget_per_attention_clp,
                "annual_budget_clp": annual_budget,
                "note": "An attention is not assumed to equal a record or Build_Id.",
            },
            "operating_cost_inputs": {
                "monthly_cloud_usd": monthly_cloud_usd,
                "monthly_ai_usd": monthly_ai_usd,
                "usd_clp_assumption": usd_clp,
                "annual_operating_cost_clp": operating_cost,
                "imputed_development_cost_clp": imputed_development_cost_clp,
            },
            "effort_scenarios": scenarios,
            "effort_monte_carlo": {
                "simulations": simulations,
                "coverage_distribution": "triangular(min=0.10, mode=0.25, max=0.50)",
                "effort_reduction_distribution": "triangular(min=0.25, mode=0.50, max=0.75)",
                "gross_benefit_clp": percentile_summary(gross_values),
                "net_benefit_clp": percentile_summary(net_values),
                "roi": percentile_summary(roi_values),
                "probability_net_benefit_above_zero": sum(value > 0 for value in net_values) / simulations,
            },
            "detection_model_normalized": {
                "unit": "per 100 records reviewed in the prioritized queue",
                "value_per_detection_distribution": (
                    f"triangular(min={budget_per_attention_clp*0.5:.0f}, mode={budget_per_attention_clp:.0f}, max={budget_per_attention_clp*4:.0f}) CLP"
                ),
                "value_clp": percentile_summary(detection_values),
                "annual_roi_not_calculated_reason": "The attention-to-build-to-record mapping is not measured.",
            },
            "break_even": {
                "minimum_coverage_times_effort_reduction": break_even_product,
                "meaning": "The product coverage × effort reduction must exceed this value for gross effort benefit to cover annual cost.",
            },
            "classification_of_inputs": {
                "measured": ["test ranking metrics", "grouped bootstrap uncertainty"],
                "budgetary": ["144 annual attentions", "CLP 224,000 per attention"],
                "assumptions": ["coverage", "effort reduction", "USD/CLP", "value per early detection"],
            },
            "interpretation": (
                "The economic case is a conditional ex-ante projection. It quantifies when the project would create value; it does not claim that savings have already been realized."
            ),
            "next_gate": "Integrate CLI and run the complete test suite before documentation freeze.",
        }
        (output_dir / "economic_evaluation_v3.json").write_text(
            json.dumps(evaluation, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return evaluation
