"""Auditable explanations for the configuration-only v2 models."""

from __future__ import annotations

import csv
import html
import json
import random
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import roc_auc_score

from performance_decision_engine.infrastructure.configuration_training_v2 import (
    FEATURES,
    NOT_APPLIES,
    RANDOM_STATE,
    ConfigurationTrainingV2,
    eligibility_reason,
    feature_row,
    technical_label,
)


def percentile_summary(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("At least one value is required")
    return {
        "mean": float(np.mean(values)),
        "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        "lower_95": float(np.quantile(values, 0.025)),
        "upper_95": float(np.quantile(values, 0.975)),
    }


def permute_feature_by_group(
    values: list[list[str]],
    groups: list[str],
    feature_index: int,
    generator: random.Random,
) -> list[list[str]]:
    """Shuffle a feature in Build_Id blocks instead of independent rows."""
    copied = [list(row) for row in values]
    by_group: dict[str, list[int]] = {}
    for index, group in enumerate(groups):
        by_group.setdefault(group, []).append(index)
    recipients = sorted(by_group)
    donors = recipients.copy()
    generator.shuffle(donors)
    for recipient, donor in zip(recipients, donors, strict=True):
        recipient_indexes = by_group[recipient]
        donor_indexes = by_group[donor]
        donor_values = [values[index][feature_index] for index in donor_indexes]
        for position, index in enumerate(recipient_indexes):
            copied[index][feature_index] = donor_values[position % len(donor_values)]
    return copied


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _bar_chart_svg(
    path: Path, rows: list[dict[str, object]], title: str, value_key: str
) -> None:
    width, height = 920, 420
    left, top, chart_width = 210, 75, 630
    values = [float(row[value_key]) for row in rows]
    extent = max(max(abs(value) for value in values), 0.01)
    zero = left + chart_width / 2
    scale = (chart_width / 2 - 30) / extent
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="40" y="38" font-family="Arial" font-size="24" font-weight="700" fill="#073b66">{html.escape(title)}</text>',
        f'<line x1="{zero:.1f}" y1="60" x2="{zero:.1f}" y2="365" stroke="#718096" stroke-width="1"/>',
    ]
    for position, row in enumerate(rows):
        y = top + position * 88
        value = float(row[value_key])
        bar_x = zero if value >= 0 else zero + value * scale
        bar_width = abs(value * scale)
        color = "#009e95" if value >= 0 else "#d9534f"
        elements.extend(
            [
                f'<text x="35" y="{y + 25}" font-family="Arial" font-size="20" fill="#17324d">{html.escape(str(row["feature"]))}</text>',
                f'<rect x="{bar_x:.1f}" y="{y}" width="{bar_width:.1f}" height="32" rx="5" fill="{color}"/>',
                f'<text x="{(zero + value * scale + (8 if value >= 0 else -8)):.1f}" y="{y + 23}" text-anchor="{"start" if value >= 0 else "end"}" font-family="Arial" font-size="17" font-weight="700" fill="#17324d">{value:.3f}</text>',
            ]
        )
    elements.append(
        '<text x="460" y="400" text-anchor="middle" font-family="Arial" font-size="16" fill="#4a5568">Caída de ROC-AUC al permutar · valores positivos indican aporte predictivo</text>'
    )
    elements.append("</svg>")
    path.write_text("\n".join(elements), encoding="utf-8")


class ConfigurationExplainabilityV2:
    def __init__(self) -> None:
        self.training = ConfigurationTrainingV2()

    def _permutation_importance(
        self,
        model: Any,
        x_holdout: list[list[str]],
        y_holdout: list[str],
        groups: list[str],
        repetitions: int,
    ) -> tuple[float, list[dict[str, object]]]:
        expected = [1 if value == NOT_APPLIES else 0 for value in y_holdout]
        baseline_probabilities = self.training._probabilities(model, x_holdout)
        baseline_auc = float(roc_auc_score(expected, baseline_probabilities))
        generator = random.Random(RANDOM_STATE)
        output: list[dict[str, object]] = []
        for feature_index, feature in enumerate(FEATURES):
            drops: list[float] = []
            for _ in range(repetitions):
                permuted = permute_feature_by_group(
                    x_holdout, groups, feature_index, generator
                )
                probabilities = self.training._probabilities(model, permuted)
                drops.append(baseline_auc - float(roc_auc_score(expected, probabilities)))
            output.append(
                {
                    "feature": feature,
                    "baseline_roc_auc": baseline_auc,
                    "repetitions": repetitions,
                    **percentile_summary(drops),
                }
            )
        output.sort(key=lambda row: float(row["mean"]), reverse=True)
        return baseline_auc, output

    def _risk_profiles(
        self, model: Any, x_holdout: list[list[str]]
    ) -> list[dict[str, object]]:
        output: list[dict[str, object]] = []
        for feature_index, feature in enumerate(FEATURES):
            levels = sorted({row[feature_index] for row in x_holdout})
            for level in levels:
                counterfactual = [list(row) for row in x_holdout]
                for row in counterfactual:
                    row[feature_index] = level
                probabilities = self.training._probabilities(model, counterfactual)
                output.append(
                    {
                        "feature": feature,
                        "level": level,
                        "holdout_support": sum(
                            row[feature_index] == level for row in x_holdout
                        ),
                        "mean_predicted_not_applies_probability": float(
                            np.mean(probabilities)
                        ),
                        "interpretation": "diagnostic association; not a causal effect",
                    }
                )
        return output

    @staticmethod
    def _logistic_coefficients(model: Any) -> list[dict[str, object]]:
        preprocessor = model.named_steps["preprocessor"]
        encoder = preprocessor.named_transformers_["configuration"]
        names: list[str] = []
        for feature, categories in zip(FEATURES, encoder.categories_, strict=True):
            names.extend(f"{feature}={category}" for category in categories)
        classifier = model.named_steps["classifier"]
        classes = list(classifier.classes_)
        coefficients = classifier.coef_[0]
        if len(classes) == 2 and classes[1] != NOT_APPLIES:
            coefficients = -coefficients
        rows = [
            {
                "encoded_feature": name,
                "coefficient_for_not_applies": float(coefficient),
                "odds_ratio": float(np.exp(coefficient)),
            }
            for name, coefficient in zip(names, coefficients, strict=True)
        ]
        rows.sort(key=lambda row: abs(float(row["coefficient_for_not_applies"])), reverse=True)
        return rows

    def run(
        self,
        source_path: Path,
        output_dir: Path,
        permutation_repetitions: int = 50,
    ) -> dict[str, object]:
        rows = self.training.read_fixed_width(source_path)
        usable = [row for row in rows if eligibility_reason(row) == "trainable"]
        features = [feature_row(row) for row in usable]
        labels = [technical_label(row) for row in usable]
        groups = [row["Build_Id"] for row in usable]
        train_i, holdout_i = self.training._split(labels, groups)
        x_train = [features[index] for index in train_i]
        y_train = [labels[index] for index in train_i]
        x_holdout = [features[index] for index in holdout_i]
        y_holdout = [labels[index] for index in holdout_i]
        holdout_groups = [groups[index] for index in holdout_i]

        candidates = self.training.candidates()
        random_forest = candidates["random_forest"].fit(x_train, y_train)
        logistic = candidates["logistic_regression"].fit(x_train, y_train)
        baseline_auc, importance = self._permutation_importance(
            random_forest,
            x_holdout,
            y_holdout,
            holdout_groups,
            permutation_repetitions,
        )
        profiles = self._risk_profiles(random_forest, x_holdout)
        coefficients = self._logistic_coefficients(logistic)

        output_dir.mkdir(parents=True, exist_ok=True)
        _write_csv(output_dir / "grouped_permutation_importance_v2.csv", importance)
        _write_csv(output_dir / "configuration_risk_profiles_v2.csv", profiles)
        _write_csv(output_dir / "logistic_coefficients_v2.csv", coefficients)
        _bar_chart_svg(
            output_dir / "grouped_permutation_importance_v2.svg",
            importance,
            "Importancia agrupada del Random Forest v2",
            "mean",
        )

        report: dict[str, object] = {
            "schema_version": "1.0",
            "experiment": "configuration_v2_explainability",
            "source": str(source_path),
            "training_rows": len(usable),
            "features": list(FEATURES),
            "split": {
                "random_state": RANDOM_STATE,
                "train_rows": len(train_i),
                "holdout_rows": len(holdout_i),
                "holdout_builds": len(set(holdout_groups)),
                "group_overlap": 0,
            },
            "random_forest_grouped_permutation_importance": {
                "scoring": "ROC-AUC for not_applies",
                "baseline_roc_auc": baseline_auc,
                "repetitions": permutation_repetitions,
                "permutation_unit": "Build_Id block",
                "results": importance,
                "interpretation": (
                    "Positive mean drop indicates predictive contribution. Intervals that "
                    "include zero indicate uncertain importance."
                ),
            },
            "risk_profiles": {
                "method": "replace one configuration level across holdout and average predictions",
                "warning": "Associational diagnostic only; it does not establish causality.",
                "results": profiles,
            },
            "logistic_reference": {
                "class": NOT_APPLIES,
                "coefficient_interpretation": (
                    "Positive coefficient and odds ratio above 1 increase model odds of "
                    "not_applies relative to the encoded alternatives."
                ),
                "warning": (
                    "One-hot coefficients are conditional on all encoded columns and should "
                    "not be interpreted as causal effects."
                ),
                "coefficients": coefficients,
            },
        }
        (output_dir / "configuration_explainability_v2.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report
