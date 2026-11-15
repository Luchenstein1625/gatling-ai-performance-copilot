from __future__ import annotations

import csv
import html
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.metrics import roc_auc_score

from performance_decision_engine.infrastructure.calibration_decision_v3 import CalibrationDecisionV3
from performance_decision_engine.infrastructure.configuration_training_v2 import (
    FEATURES,
    NOT_APPLIES,
    ConfigurationTrainingV2,
    eligibility_reason,
    feature_row,
    technical_label,
)
from performance_decision_engine.infrastructure.model_selection_v3 import ModelSelectionV3, sha256_file, sha256_text


RANDOM_STATE = 42
LEVEL_ORDER = {
    "Concurrency": ("very_low", "low", "medium", "high", "very_high"),
    "Iterations": ("low", "medium", "high"),
    "ResponseTime": ("very_high", "high", "medium", "low"),
}
REAL_VALUES = {
    "Concurrency": {"very_low": 5, "low": 20, "medium": 40, "high": 60, "very_high": 80},
    "Iterations": {"low": 5, "medium": 7, "high": 10},
    "ResponseTime": {"very_high": 15000, "high": 8000, "medium": 5000, "low": 3000},
}


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
    values: list[list[str]], groups: list[str], feature_index: int, generator: random.Random
) -> list[list[str]]:
    copied = [list(row) for row in values]
    by_group: dict[str, list[int]] = defaultdict(list)
    for index, group in enumerate(groups):
        by_group[group].append(index)
    recipients = sorted(by_group)
    donors = recipients.copy()
    generator.shuffle(donors)
    for recipient, donor in zip(recipients, donors, strict=True):
        donor_values = [values[index][feature_index] for index in by_group[donor]]
        for position, index in enumerate(by_group[recipient]):
            copied[index][feature_index] = donor_values[position % len(donor_values)]
    return copied


def bootstrap_group_indexes(groups: list[str], generator: random.Random) -> tuple[list[int], list[str]]:
    by_group: dict[str, list[int]] = defaultdict(list)
    for index, group in enumerate(groups):
        by_group[group].append(index)
    names = sorted(by_group)
    indexes: list[int] = []
    sampled_groups: list[str] = []
    for draw in range(len(names)):
        selected = generator.choice(names)
        selected_indexes = by_group[selected]
        indexes.extend(selected_indexes)
        sampled_groups.extend([f"{selected}#draw_{draw}"] * len(selected_indexes))
    return indexes, sampled_groups


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def logistic_coefficients(model: Any) -> dict[str, float]:
    preprocessor = model.named_steps["preprocessor"]
    encoder = preprocessor.named_transformers_["configuration"]
    names: list[str] = []
    for feature, categories in zip(FEATURES, encoder.categories_, strict=True):
        names.extend(f"{feature}={category}" for category in categories)
    classifier = model.named_steps["classifier"]
    coefficients = classifier.coef_[0]
    if list(classifier.classes_)[1] != NOT_APPLIES:
        coefficients = -coefficients
    return {name: float(value) for name, value in zip(names, coefficients, strict=True)}


def importance_svg(path: Path, rows: list[dict[str, Any]]) -> None:
    selected = [row for row in rows if row["model_variant"] == "train_only_replica_on_dev_oos"]
    width, height = 940, 430
    left, top, chart_width = 220, 90, 620
    extent = max([abs(float(row["mean_drop_roc_auc"])) for row in selected] + [0.01])
    scale = (chart_width - 80) / extent
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="35" y="42" font-family="Arial" font-size="24" font-weight="700" fill="#073b66">Importancia agrupada · modelo v3 · dev fuera de muestra</text>',
    ]
    for position, row in enumerate(selected):
        y = top + position * 92
        mean = float(row["mean_drop_roc_auc"])
        low = float(row["lower_95"])
        high = float(row["upper_95"])
        x_mean = left + mean * scale
        x_low = left + low * scale
        x_high = left + high * scale
        parts.extend([
            f'<text x="25" y="{y + 9}" font-family="Arial" font-size="20" fill="#17324d">{html.escape(str(row["feature"]))}</text>',
            f'<line x1="{x_low:.1f}" y1="{y}" x2="{x_high:.1f}" y2="{y}" stroke="#6b7c8f" stroke-width="4"/>',
            f'<circle cx="{x_mean:.1f}" cy="{y}" r="9" fill="#009e95"/>',
            f'<text x="{x_high + 12:.1f}" y="{y + 7}" font-family="Arial" font-size="17" fill="#17324d">{mean:.3f} [{low:.3f}; {high:.3f}]</text>',
        ])
    parts.extend([
        f'<line x1="{left}" y1="65" x2="{left}" y2="355" stroke="#d9534f" stroke-dasharray="5 5"/>',
        '<text x="470" y="405" text-anchor="middle" font-family="Arial" font-size="16" fill="#4a5568">Caída de ROC-AUC al permutar por Build_Id · IC95% bootstrap agrupado</text>',
        '</svg>',
    ])
    path.write_text("\n".join(parts), encoding="utf-8")


class FinalModelExplainabilityV31:
    def __init__(self) -> None:
        self.training = ConfigurationTrainingV2()
        self.selection = ModelSelectionV3()
        self.calibration = CalibrationDecisionV3()

    @staticmethod
    def _assignments(path: Path) -> dict[str, str]:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            return {row["build_id_sha256"]: row["partition"] for row in csv.DictReader(source)}

    def _probabilities(self, artifact: dict[str, Any], values: list[list[str]]) -> list[float]:
        raw = self.selection._probabilities(artifact["pipeline"], values)
        return self.calibration._apply_calibrator(
            artifact["calibrator"], str(artifact["calibration_method"]), raw
        )

    def _importance(
        self,
        variant: str,
        artifact: dict[str, Any],
        x_dev: list[list[str]],
        y_dev: list[str],
        g_dev: list[str],
        permutations: int,
        bootstrap: int,
    ) -> tuple[float, list[dict[str, Any]]]:
        expected = [int(label == NOT_APPLIES) for label in y_dev]
        baseline = float(roc_auc_score(expected, self._probabilities(artifact, x_dev)))
        generator = random.Random(RANDOM_STATE)
        permutation_drops: dict[str, list[float]] = {feature: [] for feature in FEATURES}
        for feature_index, feature in enumerate(FEATURES):
            for _ in range(permutations):
                permuted = permute_feature_by_group(x_dev, g_dev, feature_index, generator)
                auc = float(roc_auc_score(expected, self._probabilities(artifact, permuted)))
                permutation_drops[feature].append(baseline - auc)

        bootstrap_drops: dict[str, list[float]] = {feature: [] for feature in FEATURES}
        for _ in range(bootstrap):
            indexes, sampled_groups = bootstrap_group_indexes(g_dev, generator)
            sample_x = [x_dev[index] for index in indexes]
            sample_y = [expected[index] for index in indexes]
            if len(set(sample_y)) < 2:
                continue
            sample_base = float(roc_auc_score(sample_y, self._probabilities(artifact, sample_x)))
            for feature_index, feature in enumerate(FEATURES):
                permuted = permute_feature_by_group(sample_x, sampled_groups, feature_index, generator)
                auc = float(roc_auc_score(sample_y, self._probabilities(artifact, permuted)))
                bootstrap_drops[feature].append(sample_base - auc)

        rows = []
        for feature in FEATURES:
            permutation = percentile_summary(permutation_drops[feature])
            grouped = percentile_summary(bootstrap_drops[feature])
            rows.append({
                "version_label": "v3_final",
                "model_variant": variant,
                "evaluation_partition": "dev",
                "feature": feature,
                "baseline_roc_auc": baseline,
                "permutation_repetitions": permutations,
                "mean_drop_roc_auc": permutation["mean"],
                "permutation_std": permutation["std"],
                "grouped_bootstrap_repetitions": len(bootstrap_drops[feature]),
                "lower_95": grouped["lower_95"],
                "upper_95": grouped["upper_95"],
                "importance_supported": grouped["lower_95"] > 0,
            })
        rows.sort(key=lambda row: (str(row["model_variant"]), -float(row["mean_drop_roc_auc"])))
        return baseline, rows

    def _profiles(self, artifact: dict[str, Any], x_dev: list[list[str]]) -> list[dict[str, Any]]:
        output = []
        for feature_index, feature in enumerate(FEATURES):
            for rank, level in enumerate(LEVEL_ORDER[feature]):
                counterfactual = [list(row) for row in x_dev]
                for row in counterfactual:
                    row[feature_index] = level
                probabilities = self._probabilities(artifact, counterfactual)
                output.append({
                    "version_label": "v3_final",
                    "model_variant": "train_only_replica_on_dev_oos",
                    "feature": feature,
                    "strictness_rank_low_to_high": rank,
                    "level": level,
                    "real_value": REAL_VALUES[feature][level],
                    "dev_support": sum(row[feature_index] == level for row in x_dev),
                    "pdp_mean_probability_not_applies": float(np.mean(probabilities)),
                    "ice_p10": float(np.quantile(probabilities, 0.10)),
                    "ice_median": float(np.median(probabilities)),
                    "ice_p90": float(np.quantile(probabilities, 0.90)),
                    "interpretation": "associational diagnostic; not causal",
                })
        return output

    def _logistic_reference(
        self,
        x_train: list[list[str]],
        y_train: list[str],
        g_train: list[str],
        parameters: dict[str, Any],
        bootstrap: int,
    ) -> list[dict[str, Any]]:
        fitted = self.selection.build_model("logistic_regression", parameters).fit(x_train, y_train)
        point = logistic_coefficients(fitted)
        by_group: dict[str, list[int]] = defaultdict(list)
        for index, group in enumerate(g_train):
            by_group[group].append(index)
        names = sorted(by_group)
        generator = random.Random(RANDOM_STATE)
        distributions: dict[str, list[float]] = {name: [] for name in point}
        for _ in range(bootstrap):
            indexes = [index for _ in names for index in by_group[generator.choice(names)]]
            sample_x = [x_train[index] for index in indexes]
            sample_y = [y_train[index] for index in indexes]
            if len(set(sample_y)) < 2:
                continue
            model = self.selection.build_model("logistic_regression", parameters).fit(sample_x, sample_y)
            values = logistic_coefficients(model)
            for name in distributions:
                if name in values:
                    distributions[name].append(values[name])
        rows = []
        for name, coefficient in point.items():
            interval = percentile_summary(distributions[name])
            rows.append({
                "version_label": "v3_logistic_reference",
                "training_partition": "train",
                "encoded_feature": name,
                "coefficient_for_not_applies": coefficient,
                "odds_ratio": float(np.exp(coefficient)),
                "coefficient_lower_95": interval["lower_95"],
                "coefficient_upper_95": interval["upper_95"],
                "odds_ratio_lower_95": float(np.exp(interval["lower_95"])),
                "odds_ratio_upper_95": float(np.exp(interval["upper_95"])),
                "bootstrap_repetitions": len(distributions[name]),
                "direction_supported": interval["lower_95"] > 0 or interval["upper_95"] < 0,
                "interpretation": "conditional association in regularized contrast model; not causal",
            })
        rows.sort(key=lambda row: abs(float(row["coefficient_for_not_applies"])), reverse=True)
        return rows

    def run(
        self,
        source_path: Path,
        protocol_path: Path,
        assignments_path: Path,
        governance_addendum_path: Path,
        selection_report_path: Path,
        calibration_report_path: Path,
        final_model_path: Path,
        output_dir: Path,
        permutations: int = 50,
        bootstrap: int = 500,
    ) -> dict[str, Any]:
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        addendum = json.loads(governance_addendum_path.read_text(encoding="utf-8"))
        selection_report = json.loads(selection_report_path.read_text(encoding="utf-8"))
        calibration_report = json.loads(calibration_report_path.read_text(encoding="utf-8"))
        if sha256_file(source_path) != protocol.get("source_sha256"):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        if not any(item.get("id") == "A6" for item in addendum.get("registered_analyses", [])):
            raise ValueError("A6 explainability is not pre-registered")
        if calibration_report.get("test_status") != "LOCKED_NOT_EVALUATED":
            raise ValueError("Calibration selection did not preserve test lock")
        if calibration_report.get("selected_model") != "random_forest":
            raise ValueError("Frozen final model is not the expected Random Forest")

        assignments = self._assignments(assignments_path)
        rows = [row for row in self.training.read_fixed_width(source_path) if eligibility_reason(row) == "trainable"]
        partitions: dict[str, list[dict[str, str]]] = {"train": [], "dev": [], "test": []}
        for row in rows:
            partition = assignments.get(sha256_text(row["Build_Id"]))
            if partition not in partitions:
                raise ValueError("Eligible Build_Id missing from v3 assignment")
            partitions[partition].append(row)
        train, dev = partitions["train"], partitions["dev"]
        x_train, y_train, g_train = (
            [feature_row(row) for row in train], [technical_label(row) for row in train], [row["Build_Id"] for row in train]
        )
        x_dev, y_dev, g_dev = (
            [feature_row(row) for row in dev], [technical_label(row) for row in dev], [row["Build_Id"] for row in dev]
        )

        final_artifact = joblib.load(final_model_path)
        parameters = dict(calibration_report["selected_parameters"])
        calibration_method = str(calibration_report["selected_calibration"])
        train_oof = self.calibration._oof_probabilities("random_forest", parameters, x_train, y_train, g_train)
        train_calibrator = self.calibration._fit_calibrator(calibration_method, train_oof, y_train)
        train_model = self.selection.build_model("random_forest", parameters).fit(x_train, y_train)
        train_only_artifact = {
            "pipeline": train_model,
            "calibrator": train_calibrator,
            "calibration_method": calibration_method,
        }

        final_auc, final_importance = self._importance(
            "final_refit_train_plus_dev_on_dev_descriptive", final_artifact,
            x_dev, y_dev, g_dev, permutations, bootstrap,
        )
        oos_auc, oos_importance = self._importance(
            "train_only_replica_on_dev_oos", train_only_artifact,
            x_dev, y_dev, g_dev, permutations, bootstrap,
        )
        importance = final_importance + oos_importance
        profiles = self._profiles(train_only_artifact, x_dev)
        logistic_parameters = selection_report["best_by_model"]["logistic_regression"]["parameters"]
        if isinstance(logistic_parameters, str):
            logistic_parameters = json.loads(logistic_parameters)
        coefficients = self._logistic_reference(
            x_train, y_train, g_train, dict(logistic_parameters), bootstrap
        )

        output_dir.mkdir(parents=True, exist_ok=True)
        _write_csv(output_dir / "grouped_permutation_importance_v3.csv", importance)
        _write_csv(output_dir / "pdp_ice_v3.csv", profiles)
        _write_csv(output_dir / "logistic_coefficients_v3.csv", coefficients)
        importance_svg(output_dir / "grouped_permutation_importance_v3.svg", importance)
        report = {
            "schema_version": "3.1",
            "alert": "A6",
            "status": "FINAL_MODEL_EXPLAINABILITY_COMPLETE",
            "test_status": "NOT_ACCESSED_DEV_EXPLANATION_ONLY",
            "features": list(FEATURES),
            "rows": {"train": len(train), "train_builds": len(set(g_train)), "dev": len(dev), "dev_builds": len(set(g_dev))},
            "model": {"name": "random_forest", "parameters": parameters, "calibration": calibration_method},
            "variants": {
                "final_refit_train_plus_dev_on_dev_descriptive": {
                    "baseline_dev_roc_auc": final_auc,
                    "warning": "Dev participated in final refit; use for exact-artifact explanation, not performance estimation.",
                },
                "train_only_replica_on_dev_oos": {
                    "baseline_dev_roc_auc": oos_auc,
                    "use": "primary out-of-sample explainability sensitivity with frozen parameters.",
                },
            },
            "importance_scoring": "ROC-AUC decrease for not_applies after Build_Id-block permutation",
            "permutation_repetitions": permutations,
            "grouped_bootstrap_repetitions": bootstrap,
            "response_time_order": "very_high 15000 -> high 8000 -> medium 5000 -> low 3000; lower milliseconds is stricter",
            "causal_claim": False,
            "official_v3_changed": False,
        }
        (output_dir / "final_model_explainability_v3.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report

