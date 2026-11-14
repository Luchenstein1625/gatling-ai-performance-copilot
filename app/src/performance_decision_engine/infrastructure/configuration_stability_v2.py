"""Grouped uncertainty and stability analysis for configuration training v2."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.model_selection import GroupShuffleSplit

from performance_decision_engine.infrastructure.configuration_training_v2 import (
    APPLIES,
    NOT_APPLIES,
    RANDOM_STATE,
    TEST_SIZE,
    ConfigurationTrainingV2,
    eligibility_reason,
    feature_row,
    technical_label,
)

MODELS = ("logistic_regression", "random_forest")
METRICS = ("macro_f1", "roc_auc", "pr_auc", "recall_at_30", "precision_at_30")


def percentile_interval(values: list[float], confidence: float = 0.95) -> dict[str, float]:
    if not values:
        raise ValueError("At least one value is required")
    alpha = (1.0 - confidence) / 2.0
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "lower": float(np.quantile(values, alpha)),
        "upper": float(np.quantile(values, 1.0 - alpha)),
    }


def grouped_bootstrap_indexes(
    groups: list[str], repetitions: int, seed: int = RANDOM_STATE
) -> list[list[int]]:
    """Sample Build_Id groups with replacement, preserving every row in each group."""
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    by_group: dict[str, list[int]] = {}
    for index, group in enumerate(groups):
        by_group.setdefault(group, []).append(index)
    names = sorted(by_group)
    if len(names) < 2:
        raise ValueError("At least two Build_Id groups are required")
    generator = random.Random(seed)
    samples: list[list[int]] = []
    for _ in range(repetitions):
        selected = [generator.choice(names) for _ in names]
        samples.append([index for name in selected for index in by_group[name]])
    return samples


class ConfigurationStabilityV2:
    def __init__(self) -> None:
        self.training = ConfigurationTrainingV2()

    @staticmethod
    def _valid_group_split(
        labels: list[str], groups: list[str], seed: int
    ) -> tuple[list[int], list[int]]:
        indexes = list(range(len(labels)))
        splitter = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=seed)
        train, holdout = next(splitter.split(indexes, labels, groups))
        train_i, holdout_i = train.tolist(), holdout.tolist()
        if set(labels[index] for index in train_i) != {APPLIES, NOT_APPLIES}:
            raise ValueError(f"Seed {seed} produced a one-class train split")
        if set(labels[index] for index in holdout_i) != {APPLIES, NOT_APPLIES}:
            raise ValueError(f"Seed {seed} produced a one-class holdout split")
        return train_i, holdout_i

    def _fit_models(
        self,
        features: list[list[str]],
        labels: list[str],
        groups: list[str],
        train_i: list[int],
        holdout_i: list[int],
    ) -> dict[str, dict[str, Any]]:
        x_train = [features[index] for index in train_i]
        y_train = [labels[index] for index in train_i]
        g_train = [groups[index] for index in train_i]
        x_holdout = [features[index] for index in holdout_i]
        y_holdout = [labels[index] for index in holdout_i]
        output: dict[str, dict[str, Any]] = {}
        candidates = self.training.candidates()
        for name in MODELS:
            candidate = candidates[name]
            oof_probabilities = self.training._oof(candidate, x_train, y_train, g_train)
            threshold = self.training._best_threshold(y_train, oof_probabilities)
            fitted = candidate.fit(x_train, y_train)
            holdout_probabilities = self.training._probabilities(fitted, x_holdout)
            output[name] = {
                "threshold": threshold,
                "metrics": self.training._metrics(
                    y_holdout, holdout_probabilities, threshold
                ),
                "probabilities": holdout_probabilities,
                "expected": y_holdout,
                "groups": [groups[index] for index in holdout_i],
            }
        return output

    def _repeated_splits(
        self,
        features: list[list[str]],
        labels: list[str],
        groups: list[str],
        repetitions: int,
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for seed in range(RANDOM_STATE, RANDOM_STATE + repetitions):
            train_i, holdout_i = self._valid_group_split(labels, groups, seed)
            reports = self._fit_models(features, labels, groups, train_i, holdout_i)
            for name in MODELS:
                metrics = reports[name]["metrics"]
                rows.append(
                    {
                        "seed": seed,
                        "model": name,
                        "threshold_oof": reports[name]["threshold"],
                        "train_rows": len(train_i),
                        "holdout_rows": len(holdout_i),
                        "train_builds": len({groups[index] for index in train_i}),
                        "holdout_builds": len({groups[index] for index in holdout_i}),
                        **{metric: metrics[metric] for metric in METRICS},
                    }
                )
        return rows

    def _paired_bootstrap(
        self, reports: dict[str, dict[str, Any]], repetitions: int
    ) -> list[dict[str, object]]:
        reference = reports["random_forest"]
        samples = grouped_bootstrap_indexes(reference["groups"], repetitions)
        rows: list[dict[str, object]] = []
        for repetition, indexes in enumerate(samples, start=1):
            expected = [reference["expected"][index] for index in indexes]
            if len(set(expected)) < 2:
                continue
            row: dict[str, object] = {"repetition": repetition}
            metric_values: dict[str, dict[str, float]] = {}
            for name in MODELS:
                probabilities = [reports[name]["probabilities"][index] for index in indexes]
                metrics = self.training._metrics(
                    expected, probabilities, float(reports[name]["threshold"])
                )
                metric_values[name] = {metric: float(metrics[metric]) for metric in METRICS}
                for metric in METRICS:
                    row[f"{name}_{metric}"] = metric_values[name][metric]
            for metric in METRICS:
                row[f"delta_rf_minus_logistic_{metric}"] = (
                    metric_values["random_forest"][metric]
                    - metric_values["logistic_regression"][metric]
                )
            rows.append(row)
        return rows

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
        if not rows:
            raise ValueError(f"No rows to write: {path}")
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def run(
        self,
        source_path: Path,
        output_dir: Path,
        split_repetitions: int = 20,
        bootstrap_repetitions: int = 1000,
    ) -> dict[str, object]:
        rows = self.training.read_fixed_width(source_path)
        usable = [row for row in rows if eligibility_reason(row) == "trainable"]
        features = [feature_row(row) for row in usable]
        labels = [technical_label(row) for row in usable]
        groups = [row["Build_Id"] for row in usable]

        fixed_train, fixed_holdout = self.training._split(labels, groups)
        fixed_reports = self._fit_models(
            features, labels, groups, fixed_train, fixed_holdout
        )
        repeated_rows = self._repeated_splits(
            features, labels, groups, split_repetitions
        )
        bootstrap_rows = self._paired_bootstrap(fixed_reports, bootstrap_repetitions)

        repeated_summary: dict[str, object] = {}
        for name in MODELS:
            model_rows = [row for row in repeated_rows if row["model"] == name]
            repeated_summary[name] = {
                metric: percentile_interval([float(row[metric]) for row in model_rows])
                for metric in METRICS
            }

        bootstrap_summary: dict[str, object] = {}
        for name in MODELS:
            bootstrap_summary[name] = {
                metric: percentile_interval(
                    [float(row[f"{name}_{metric}"]) for row in bootstrap_rows]
                )
                for metric in METRICS
            }
        paired_differences = {
            metric: percentile_interval(
                [
                    float(row[f"delta_rf_minus_logistic_{metric}"])
                    for row in bootstrap_rows
                ]
            )
            for metric in METRICS
        }

        report: dict[str, object] = {
            "schema_version": "1.0",
            "experiment": "configuration_v2_grouped_stability",
            "source": str(source_path),
            "training_rows": len(usable),
            "builds": len(set(groups)),
            "models": list(MODELS),
            "fixed_split": {
                "random_state": RANDOM_STATE,
                "train_rows": len(fixed_train),
                "holdout_rows": len(fixed_holdout),
                "train_builds": len({groups[index] for index in fixed_train}),
                "holdout_builds": len({groups[index] for index in fixed_holdout}),
                "group_overlap": 0,
                "point_estimates": {
                    name: {
                        "threshold_oof": fixed_reports[name]["threshold"],
                        **{
                            metric: fixed_reports[name]["metrics"][metric]
                            for metric in METRICS
                        },
                    }
                    for name in MODELS
                },
            },
            "repeated_group_splits": {
                "repetitions": split_repetitions,
                "seeds": [RANDOM_STATE, RANDOM_STATE + split_repetitions - 1],
                "summary": repeated_summary,
            },
            "grouped_paired_bootstrap": {
                "requested_repetitions": bootstrap_repetitions,
                "valid_repetitions": len(bootstrap_rows),
                "confidence_level": 0.95,
                "summary": bootstrap_summary,
                "rf_minus_logistic": paired_differences,
                "interpretation": (
                    "A paired-difference interval containing zero does not establish that "
                    "Random Forest outperforms logistic regression on that metric."
                ),
            },
            "limitations": [
                "Repeated splits are a stability diagnostic, not new independent data.",
                "The fixed holdout remains the reported final split and is reused here only "
                "for grouped uncertainty estimation.",
                "Online validation with future builds remains required.",
            ],
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        self._write_csv(output_dir / "repeated_group_splits_v2.csv", repeated_rows)
        self._write_csv(output_dir / "paired_group_bootstrap_v2.csv", bootstrap_rows)
        (output_dir / "configuration_stability_v2.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report
