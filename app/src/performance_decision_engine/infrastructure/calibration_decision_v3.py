"""Calibration and final candidate decision using frozen train/dev only."""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path
from statistics import NormalDist
from typing import Any, Callable

import joblib
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupKFold

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
BOOTSTRAP_REPETITIONS = 1000


def percentile_interval(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("At least one value is required")
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "lower_95": float(np.quantile(values, 0.025)),
        "upper_95": float(np.quantile(values, 0.975)),
    }


def wilson_interval(successes: int, total: int, confidence: float = 0.95) -> dict[str, float | int | None]:
    if total == 0:
        return {"successes": successes, "total": total, "estimate": None, "lower": None, "upper": None}
    z = NormalDist().inv_cdf(1 - (1 - confidence) / 2)
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return {
        "successes": successes,
        "total": total,
        "estimate": proportion,
        "lower": max(0.0, centre - margin),
        "upper": min(1.0, centre + margin),
    }


def expected_calibration_error(expected: list[int], probabilities: list[float], bins: int = 10) -> tuple[float, list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    error = 0.0
    for index in range(bins):
        lower, upper = index / bins, (index + 1) / bins
        selected = [i for i, value in enumerate(probabilities) if lower <= value < upper or (index == bins - 1 and value == 1.0)]
        if not selected:
            continue
        mean_probability = float(np.mean([probabilities[i] for i in selected]))
        observed = float(np.mean([expected[i] for i in selected]))
        weight = len(selected) / len(expected)
        error += weight * abs(mean_probability - observed)
        rows.append({"bin_lower": lower, "bin_upper": upper, "rows": len(selected), "mean_probability": mean_probability, "observed_rate": observed, "absolute_gap": abs(mean_probability - observed)})
    return error, rows


class CalibrationDecisionV3:
    def __init__(self) -> None:
        self.selection = ModelSelectionV3()

    @staticmethod
    def _load_assignments(path: Path) -> dict[str, str]:
        with path.open("r", encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        return {row["build_id_sha256"]: row["partition"] for row in rows}

    def _oof_probabilities(
        self,
        model_name: str,
        parameters: dict[str, object],
        features: list[list[str]],
        labels: list[str],
        groups: list[str],
    ) -> list[float]:
        output = [0.0] * len(labels)
        splitter = GroupKFold(n_splits=5)
        for train, validation in splitter.split(features, labels, groups):
            model = self.selection.build_model(model_name, parameters)
            model.fit([features[i] for i in train], [labels[i] for i in train])
            probabilities = self.selection._probabilities(model, [features[i] for i in validation])
            for index, probability in zip(validation, probabilities, strict=True):
                output[int(index)] = probability
        return output

    @staticmethod
    def _fit_calibrator(method: str, probabilities: list[float], labels: list[str]) -> Any:
        expected = np.asarray([1 if value == NOT_APPLIES else 0 for value in labels])
        values = np.asarray(probabilities)
        if method == "sigmoid":
            calibrator = LogisticRegression(C=1e6, max_iter=2000, random_state=RANDOM_STATE)
            calibrator.fit(values.reshape(-1, 1), expected)
            return calibrator
        if method == "isotonic":
            calibrator = IsotonicRegression(out_of_bounds="clip")
            calibrator.fit(values, expected)
            return calibrator
        raise ValueError(f"Unknown calibration method: {method}")

    @staticmethod
    def _apply_calibrator(calibrator: Any | None, method: str, probabilities: list[float]) -> list[float]:
        if method == "raw":
            return list(probabilities)
        values = np.asarray(probabilities)
        if method == "sigmoid":
            return [float(row[1]) for row in calibrator.predict_proba(values.reshape(-1, 1))]
        if method == "isotonic":
            return [float(value) for value in calibrator.predict(values)]
        raise ValueError(f"Unknown calibration method: {method}")

    @staticmethod
    def _calibration_metrics(labels: list[str], probabilities: list[float]) -> tuple[dict[str, float], list[dict[str, object]]]:
        expected = [1 if value == NOT_APPLIES else 0 for value in labels]
        ece, bins = expected_calibration_error(expected, probabilities)
        return ({
            "roc_auc": float(roc_auc_score(expected, probabilities)),
            "pr_auc": float(average_precision_score(expected, probabilities)),
            "brier": float(brier_score_loss(expected, probabilities)),
            "ece_10_bins": float(ece),
        }, bins)

    @staticmethod
    def _group_samples(groups: list[str], repetitions: int) -> list[list[int]]:
        by_group: dict[str, list[int]] = {}
        for index, group in enumerate(groups):
            by_group.setdefault(group, []).append(index)
        names = sorted(by_group)
        generator = random.Random(RANDOM_STATE)
        samples: list[list[int]] = []
        for _ in range(repetitions):
            selected = [generator.choice(names) for _ in names]
            samples.append([index for name in selected for index in by_group[name]])
        return samples

    def _paired_model_bootstrap(
        self,
        labels: list[str],
        groups: list[str],
        probabilities: dict[str, list[float]],
        repetitions: int,
    ) -> tuple[list[dict[str, object]], dict[str, object]]:
        rows: list[dict[str, object]] = []
        for repetition, indexes in enumerate(self._group_samples(groups, repetitions), start=1):
            expected = [1 if labels[i] == NOT_APPLIES else 0 for i in indexes]
            if len(set(expected)) < 2:
                continue
            rf = [probabilities["random_forest"][i] for i in indexes]
            boosting = [probabilities["hist_gradient_boosting"][i] for i in indexes]
            rf_auc = float(roc_auc_score(expected, rf))
            boosting_auc = float(roc_auc_score(expected, boosting))
            rows.append({"repetition": repetition, "random_forest_roc_auc": rf_auc, "hist_gradient_boosting_roc_auc": boosting_auc, "delta_boosting_minus_rf": boosting_auc - rf_auc})
        interval = percentile_interval([float(row["delta_boosting_minus_rf"]) for row in rows])
        return rows, interval

    def _threshold_analysis(self, labels: list[str], probabilities: list[float]) -> list[dict[str, object]]:
        rows = self.selection.threshold_rows(labels, probabilities)
        applies = sum(value == APPLIES for value in labels)
        review_all_cost = len(labels) + ERROR_COSTS["applies_reviewed"] * applies
        for row in rows:
            liberated = len(labels) - int(row["manual_reviews"])
            errors = int(row["false_applies"])
            interval = wilson_interval(errors, liberated)
            row["review_all_cost_units"] = review_all_cost
            row["delta_vs_review_all"] = float(row["total_cost_units"]) - review_all_cost
            row["released_rows"] = liberated
            row["released_error_rate"] = interval["estimate"]
            row["released_error_lower_95"] = interval["lower"]
            row["released_error_upper_95"] = interval["upper"]
        return rows

    def _cost_bootstrap(
        self,
        labels: list[str],
        groups: list[str],
        probabilities: list[float],
        threshold: float,
        repetitions: int,
    ) -> tuple[list[dict[str, object]], dict[str, float]]:
        rows: list[dict[str, object]] = []
        for repetition, indexes in enumerate(self._group_samples(groups, repetitions), start=1):
            sampled_labels = [labels[i] for i in indexes]
            sampled_probabilities = [probabilities[i] for i in indexes]
            prediction = self.selection._predictions(sampled_probabilities, threshold)
            reviews = sum(value == NOT_APPLIES for value in prediction)
            false_applies = sum(a == NOT_APPLIES and p == APPLIES for a, p in zip(sampled_labels, prediction, strict=True))
            applies_reviewed = sum(a == APPLIES and p == NOT_APPLIES for a, p in zip(sampled_labels, prediction, strict=True))
            model_cost = reviews + 10 * false_applies + 2 * applies_reviewed
            review_all = len(sampled_labels) + 2 * sum(value == APPLIES for value in sampled_labels)
            rows.append({"repetition": repetition, "model_cost": model_cost, "review_all_cost": review_all, "delta_model_minus_review_all": model_cost - review_all})
        interval = percentile_interval([float(row["delta_model_minus_review_all"]) for row in rows])
        return rows, interval

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def run(
        self,
        source_path: Path,
        protocol_path: Path,
        assignments_path: Path,
        selection_report_path: Path,
        output_dir: Path,
        bootstrap_repetitions: int = BOOTSTRAP_REPETITIONS,
    ) -> dict[str, object]:
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        selection_report = json.loads(selection_report_path.read_text(encoding="utf-8"))
        if protocol["source_sha256"] != sha256_file(source_path):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        if selection_report["test_status"] != "LOCKED_NOT_EVALUATED":
            raise ValueError("Selection report indicates that test was opened")
        assignments = self._load_assignments(assignments_path)
        source_rows = self.selection.reader.read_fixed_width(source_path)
        usable = [row for row in source_rows if eligibility_reason(row) == "trainable"]
        partitions: dict[str, list[dict[str, str]]] = {"train": [], "dev": [], "test": []}
        for row in usable:
            partitions[assignments[sha256_text(row["Build_Id"])]].append(row)
        x_train = [feature_row(row) for row in partitions["train"]]
        y_train = [technical_label(row) for row in partitions["train"]]
        g_train = [row["Build_Id"] for row in partitions["train"]]
        x_dev = [feature_row(row) for row in partitions["dev"]]
        y_dev = [technical_label(row) for row in partitions["dev"]]
        g_dev = [row["Build_Id"] for row in partitions["dev"]]

        best = selection_report["best_by_model"]
        parameters = {
            name: json.loads(best[name]["parameters"])
            for name in ("random_forest", "hist_gradient_boosting")
        }
        raw_models: dict[str, Any] = {}
        raw_dev: dict[str, list[float]] = {}
        oof_train: dict[str, list[float]] = {}
        for name in parameters:
            oof_train[name] = self._oof_probabilities(name, parameters[name], x_train, y_train, g_train)
            raw_models[name] = self.selection.build_model(name, parameters[name]).fit(x_train, y_train)
            raw_dev[name] = self.selection._probabilities(raw_models[name], x_dev)

        paired_rows, paired_interval = self._paired_model_bootstrap(y_dev, g_dev, raw_dev, bootstrap_repetitions)
        boosting_superior = float(paired_interval["lower_95"]) > 0
        final_model_name = "hist_gradient_boosting" if boosting_superior else "random_forest"

        calibration_rows: list[dict[str, object]] = []
        reliability_rows: list[dict[str, object]] = []
        calibrators: dict[str, Any | None] = {"raw": None}
        calibrated_dev: dict[str, list[float]] = {"raw": raw_dev[final_model_name]}
        for method in ("sigmoid", "isotonic"):
            calibrators[method] = self._fit_calibrator(method, oof_train[final_model_name], y_train)
            calibrated_dev[method] = self._apply_calibrator(calibrators[method], method, raw_dev[final_model_name])
        for method, probabilities in calibrated_dev.items():
            metrics, bins = self._calibration_metrics(y_dev, probabilities)
            calibration_rows.append({"method": method, **metrics})
            for row in bins:
                reliability_rows.append({"method": method, **row})
        selected_calibration = min(calibration_rows, key=lambda row: (float(row["brier"]), float(row["ece_10_bins"])))["method"]
        final_probabilities = calibrated_dev[str(selected_calibration)]
        threshold_rows = self._threshold_analysis(y_dev, final_probabilities)
        selected_threshold_row = min(threshold_rows, key=lambda row: (float(row["total_cost_units"]), -float(row["macro_f1"])))
        selected_threshold = float(selected_threshold_row["threshold"])
        cost_rows, cost_interval = self._cost_bootstrap(y_dev, g_dev, final_probabilities, selected_threshold, bootstrap_repetitions)

        output_dir.mkdir(parents=True, exist_ok=True)
        self._write_csv(output_dir / "paired_bootstrap_boosting_vs_rf_dev_v3.csv", paired_rows)
        self._write_csv(output_dir / "calibration_comparison_dev_v3.csv", calibration_rows)
        self._write_csv(output_dir / "reliability_bins_dev_v3.csv", reliability_rows)
        self._write_csv(output_dir / "threshold_analysis_calibrated_dev_v3.csv", threshold_rows)
        self._write_csv(output_dir / "cost_bootstrap_dev_v3.csv", cost_rows)
        joblib.dump({
            "pipeline": raw_models[final_model_name],
            "model_name": final_model_name,
            "parameters": parameters[final_model_name],
            "calibration_method": selected_calibration,
            "calibrator": calibrators[str(selected_calibration)],
            "decision_threshold": selected_threshold,
            "features": ["Concurrency", "Iterations", "ResponseTime"],
            "status": "model_final_candidate_train_dev_selected_test_locked",
        }, output_dir / "final_candidate_v3.joblib")

        report: dict[str, object] = {
            "schema_version": "3.0",
            "experiment": "calibration_and_final_candidate_train_dev_only",
            "rows": {"train": len(x_train), "dev": len(x_dev), "test_reserved_not_evaluated": len(partitions["test"])},
            "test_status": "LOCKED_NOT_EVALUATED",
            "paired_boosting_minus_rf_dev": {
                "metric": "ROC-AUC",
                "bootstrap_unit": "Build_Id",
                "repetitions": len(paired_rows),
                "interval": paired_interval,
                "boosting_superiority_demonstrated": boosting_superior,
                "preregistered_rule": "Adopt boosting only if lower IC95% of delta is above zero.",
            },
            "selected_model": final_model_name,
            "selected_parameters": parameters[final_model_name],
            "calibration_comparison": calibration_rows,
            "selected_calibration": selected_calibration,
            "selected_threshold_dev": selected_threshold,
            "selected_threshold_result": selected_threshold_row,
            "cost_delta_model_minus_review_all_grouped_bootstrap": cost_interval,
            "release_guardrail": {
                "automatic_release_enabled": False,
                "reason": "Dev evidence is used for offline selection; independent test remains locked.",
            },
            "next_gate": "Review evidence, commit and tag model-final; then open test exactly once.",
        }
        (output_dir / "calibration_decision_v3.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report
