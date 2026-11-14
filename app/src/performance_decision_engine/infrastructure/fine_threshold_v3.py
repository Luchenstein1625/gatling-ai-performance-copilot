"""Fine dev-only threshold analysis for the frozen v3 candidate."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from performance_decision_engine.infrastructure.calibration_decision_v3 import (
    CalibrationDecisionV3,
    percentile_interval,
    wilson_interval,
)
from performance_decision_engine.infrastructure.configuration_training_v2 import (
    APPLIES,
    NOT_APPLIES,
    eligibility_reason,
    feature_row,
    technical_label,
)
from performance_decision_engine.infrastructure.model_selection_v3 import (
    ERROR_COSTS,
    ModelSelectionV3,
    sha256_file,
    sha256_text,
)

RANDOM_STATE = 42
FINE_THRESHOLDS = tuple(round(index / 100, 2) for index in range(0, 21))


def policy_counts(
    labels: list[str], probabilities: list[float], threshold: float
) -> dict[str, int | float | None]:
    """Return auditable policy counts and uncertainty for one threshold."""
    predicted = ModelSelectionV3._predictions(probabilities, threshold)
    manual_reviews = sum(value == NOT_APPLIES for value in predicted)
    released_rows = len(labels) - manual_reviews
    false_applies = sum(
        actual == NOT_APPLIES and prediction == APPLIES
        for actual, prediction in zip(labels, predicted, strict=True)
    )
    applies_reviewed = sum(
        actual == APPLIES and prediction == NOT_APPLIES
        for actual, prediction in zip(labels, predicted, strict=True)
    )
    total_cost = (
        manual_reviews * ERROR_COSTS["manual_review"]
        + false_applies * ERROR_COSTS["false_applies"]
        + applies_reviewed * ERROR_COSTS["applies_reviewed"]
    )
    review_all = len(labels) + ERROR_COSTS["applies_reviewed"] * sum(
        value == APPLIES for value in labels
    )
    risk = wilson_interval(false_applies, released_rows)
    return {
        "threshold": threshold,
        "manual_reviews": manual_reviews,
        "review_coverage": manual_reviews / len(labels),
        "released_rows": released_rows,
        "release_coverage": released_rows / len(labels),
        "false_applies": false_applies,
        "applies_reviewed": applies_reviewed,
        "total_cost_units": total_cost,
        "review_all_cost_units": review_all,
        "delta_vs_review_all": total_cost - review_all,
        "delta_percent_vs_review_all": (total_cost - review_all) / review_all,
        "released_error_rate": risk["estimate"],
        "released_error_lower_95": risk["lower"],
        "released_error_upper_95": risk["upper"],
    }


def automatic_release_gate(
    row: dict[str, object], bootstrap: dict[str, object], risk_limit: float = 0.05
) -> tuple[bool, list[str]]:
    """Apply the predeclared safety and cost gates without opening test."""
    reasons: list[str] = []
    if int(row["released_rows"]) == 0:
        reasons.append("no_rows_released")
    upper_risk = row["released_error_upper_95"]
    if upper_risk is None or float(upper_risk) > risk_limit:
        reasons.append("release_risk_not_certified")
    if float(bootstrap["upper_95"]) >= 0:
        reasons.append("cost_saving_not_strictly_below_zero")
    return not reasons, reasons


class FineThresholdV3:
    def __init__(self) -> None:
        self.selection = ModelSelectionV3()

    @staticmethod
    def _load_assignments(path: Path) -> dict[str, str]:
        with path.open("r", encoding="utf-8", newline="") as source:
            return {
                row["build_id_sha256"]: row["partition"]
                for row in csv.DictReader(source)
            }

    @staticmethod
    def _group_samples(groups: list[str], repetitions: int) -> list[list[int]]:
        by_group: dict[str, list[int]] = {}
        for index, group in enumerate(groups):
            by_group.setdefault(group, []).append(index)
        names = sorted(by_group)
        generator = random.Random(RANDOM_STATE)
        return [
            [index for name in (generator.choice(names) for _ in names) for index in by_group[name]]
            for _ in range(repetitions)
        ]

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _write_svg(path: Path, rows: list[dict[str, object]]) -> None:
        width, height = 920, 480
        left, right, top, bottom = 85, 35, 45, 75
        plot_w, plot_h = width - left - right, height - top - bottom
        values = [float(row["total_cost_units"]) for row in rows]
        review_all = float(rows[0]["review_all_cost_units"])
        y_min = min(values + [review_all]) * 0.98
        y_max = max(values + [review_all]) * 1.02

        def x(value: float) -> float:
            return left + (value / 0.20) * plot_w

        def y(value: float) -> float:
            return top + (y_max - value) / (y_max - y_min) * plot_h

        points = " ".join(
            f"{x(float(row['threshold'])):.1f},{y(float(row['total_cost_units'])):.1f}"
            for row in rows
        )
        best = min(rows, key=lambda row: float(row["total_cost_units"]))
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="white"/>',
            '<text x="85" y="25" font-family="Arial" font-size="18" font-weight="bold" fill="#073b66">Costo en dev por threshold calibrado</text>',
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#425466"/>',
            f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#425466"/>',
            f'<line x1="{left}" y1="{y(review_all):.1f}" x2="{width-right}" y2="{y(review_all):.1f}" stroke="#d1495b" stroke-width="2" stroke-dasharray="7 6"/>',
            f'<text x="{width-right-150}" y="{y(review_all)-8:.1f}" font-family="Arial" font-size="13" fill="#d1495b">Revisar todo = {review_all:.0f}</text>',
            f'<polyline points="{points}" fill="none" stroke="#009b8c" stroke-width="4"/>',
        ]
        for tick in (0.00, 0.05, 0.10, 0.15, 0.20):
            parts.append(f'<text x="{x(tick)-14:.1f}" y="{height-bottom+25}" font-family="Arial" font-size="13" fill="#263746">{tick:.2f}</text>')
        parts.extend([
            f'<circle cx="{x(float(best["threshold"])):.1f}" cy="{y(float(best["total_cost_units"])):.1f}" r="6" fill="#073b66"/>',
            f'<text x="{x(float(best["threshold"]))+10:.1f}" y="{y(float(best["total_cost_units"]))-10:.1f}" font-family="Arial" font-size="13" fill="#073b66">mínimo {float(best["threshold"]):.2f} · {float(best["total_cost_units"]):.0f}</text>',
            f'<text x="{width/2-45}" y="{height-20}" font-family="Arial" font-size="14" fill="#263746">Threshold</text>',
            f'<text transform="translate(22 {height/2+40}) rotate(-90)" font-family="Arial" font-size="14" fill="#263746">Unidades de costo</text>',
            '</svg>',
        ])
        path.write_text("\n".join(parts), encoding="utf-8")

    def _bootstrap_thresholds(
        self,
        labels: list[str],
        groups: list[str],
        probabilities: list[float],
        repetitions: int,
    ) -> list[dict[str, object]]:
        samples = self._group_samples(groups, repetitions)
        output: list[dict[str, object]] = []
        for threshold in FINE_THRESHOLDS:
            deltas: list[float] = []
            for indexes in samples:
                row = policy_counts(
                    [labels[i] for i in indexes],
                    [probabilities[i] for i in indexes],
                    threshold,
                )
                deltas.append(float(row["delta_vs_review_all"]))
            interval = percentile_interval(deltas)
            output.append({
                "threshold": threshold,
                "bootstrap_repetitions": len(deltas),
                **interval,
                "probability_cost_below_review_all": sum(value < 0 for value in deltas) / len(deltas),
                "probability_cost_at_or_below_review_all": sum(value <= 0 for value in deltas) / len(deltas),
            })
        return output

    def run(
        self,
        source_path: Path,
        protocol_path: Path,
        assignments_path: Path,
        calibration_report_path: Path,
        candidate_path: Path,
        output_dir: Path,
        bootstrap_repetitions: int = 1000,
    ) -> dict[str, object]:
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        calibration = json.loads(calibration_report_path.read_text(encoding="utf-8"))
        if protocol["source_sha256"] != sha256_file(source_path):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        if protocol["test_lock"]["opened_for_model_selection"] is not False:
            raise ValueError("Frozen protocol test lock is not intact")
        if calibration["test_status"] != "LOCKED_NOT_EVALUATED":
            raise ValueError("Calibration report indicates that test was opened")

        assignments = self._load_assignments(assignments_path)
        source_rows = self.selection.reader.read_fixed_width(source_path)
        usable = [row for row in source_rows if eligibility_reason(row) == "trainable"]
        dev = [
            row for row in usable
            if assignments.get(sha256_text(row["Build_Id"])) == "dev"
        ]
        if len(dev) != int(protocol["partitions"]["dev"]["rows"]):
            raise ValueError("Dev rows differ from frozen protocol")

        candidate: dict[str, Any] = joblib.load(candidate_path)
        if candidate.get("status") != "model_final_candidate_train_dev_selected_test_locked":
            raise ValueError("Candidate status is not eligible for fine threshold analysis")
        features = [feature_row(row) for row in dev]
        labels = [technical_label(row) for row in dev]
        groups = [row["Build_Id"] for row in dev]
        raw = self.selection._probabilities(candidate["pipeline"], features)
        probabilities = CalibrationDecisionV3._apply_calibrator(
            candidate.get("calibrator"), candidate["calibration_method"], raw
        )

        threshold_rows: list[dict[str, object]] = []
        for threshold in FINE_THRESHOLDS:
            row = policy_counts(labels, probabilities, threshold)
            metrics = self.selection.metrics(labels, probabilities, threshold)
            row.update({
                "macro_f1": metrics["macro_f1"],
                "not_applies_precision": metrics["not_applies_precision"],
                "not_applies_recall": metrics["not_applies_recall"],
            })
            threshold_rows.append(row)

        bootstrap_rows = self._bootstrap_thresholds(
            labels, groups, probabilities, bootstrap_repetitions
        )
        bootstrap_by_threshold = {
            float(row["threshold"]): row for row in bootstrap_rows
        }
        for row in threshold_rows:
            bootstrap = bootstrap_by_threshold[float(row["threshold"])]
            passed, reasons = automatic_release_gate(row, bootstrap)
            row["automatic_release_gate_passed"] = passed
            row["automatic_release_gate_reasons"] = "|".join(reasons)

        minimum = min(
            threshold_rows,
            key=lambda row: (float(row["total_cost_units"]), float(row["threshold"])),
        )
        passing = [row for row in threshold_rows if row["automatic_release_gate_passed"]]
        if passing:
            operational = min(passing, key=lambda row: float(row["total_cost_units"]))
            policy = "assisted_review_with_guardrailed_release"
        else:
            operational = None
            policy = "review_all_with_ranking_assistance"

        output_dir.mkdir(parents=True, exist_ok=True)
        self._write_csv(output_dir / "fine_threshold_analysis_dev_v3.csv", threshold_rows)
        self._write_csv(output_dir / "fine_threshold_bootstrap_dev_v3.csv", bootstrap_rows)
        self._write_svg(output_dir / "fine_threshold_cost_curve_dev_v3.svg", threshold_rows)

        report: dict[str, object] = {
            "schema_version": "3.0",
            "experiment": "fine_threshold_analysis_dev_only",
            "test_status": "LOCKED_NOT_EVALUATED",
            "candidate": {
                "model": candidate["model_name"],
                "calibration": candidate["calibration_method"],
                "previous_threshold": candidate["decision_threshold"],
            },
            "dev": {"rows": len(labels), "builds": len(set(groups))},
            "threshold_grid": {"minimum": 0.0, "maximum": 0.2, "step": 0.01},
            "cost_policy": ERROR_COSTS,
            "minimum_point_estimate": minimum,
            "minimum_point_estimate_bootstrap": bootstrap_by_threshold[float(minimum["threshold"])],
            "automatic_release_gate": {
                "risk_upper_95_maximum": 0.05,
                "cost_delta_upper_95_must_be_below_zero": True,
                "passing_thresholds": [row["threshold"] for row in passing],
            },
            "recommended_policy": policy,
            "operational_threshold": None if operational is None else operational["threshold"],
            "interpretation": (
                "No automatic release threshold is authorized; keep human review and use scores only to prioritize."
                if operational is None
                else "A threshold passed both the release-risk and grouped cost gates on dev."
            ),
            "next_gate": (
                "If evidence is accepted, commit results and create the model-final tag before opening test exactly once."
            ),
        }
        (output_dir / "fine_threshold_decision_v3.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report
