"""Leakage-resistant training experiment using only pre-execution configuration.

This module is deliberately independent from the historical production artefacts.  It
filters non-executions, trains only with Concurrency/Iterations/ResponseTime and keeps a
grouped Build_Id holdout closed until model and threshold selection finish on OOF data.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

APPLIES = "applies"
NOT_APPLIES = "not_applies"
FEATURES = ("Concurrency", "Iterations", "ResponseTime")
GROUP_COLUMN = "Build_Id"
RANDOM_STATE = 42
TEST_SIZE = 0.25
THRESHOLDS = tuple(round(value / 100, 2) for value in range(5, 96, 5))


def _number(value: str | None) -> float | None:
    try:
        return float(value) if value not in {None, ""} else None
    except (TypeError, ValueError):
        return None


def eligibility_reason(row: dict[str, str]) -> str:
    """Return trainable or an auditable abstention reason."""
    if not row.get(GROUP_COLUMN):
        return "missing_build_id"
    if row.get("Performance") != "1":
        return "not_executed"
    if any(not row.get(name) for name in FEATURES):
        return "incomplete_configuration"
    errors = _number(row.get("errorCount"))
    successes = _number(row.get("successCount"))
    status = row.get("Estado", "").strip().lower()
    if errors is None or successes is None or not status:
        return "incomplete_result_evidence"
    return "trainable"


def technical_label(row: dict[str, str]) -> str:
    """Label an executed row from measured technical evidence only."""
    if eligibility_reason(row) != "trainable":
        raise ValueError("technical_label requires a trainable executed row")
    errors = float(row["errorCount"])
    successes = float(row["successCount"])
    status_ok = row["Estado"].strip().lower() == "success"
    return APPLIES if status_ok and errors == 0 and successes > 0 else NOT_APPLIES


def feature_row(row: dict[str, str]) -> list[str]:
    return [row[name] for name in FEATURES]


class ConfigurationTrainingV2:
    """Train and evaluate ex-ante configuration models without target proxies."""

    @staticmethod
    def read_fixed_width(source_path: Path) -> list[dict[str, str]]:
        if not source_path.exists():
            raise ValueError(f"Historical dataset does not exist: {source_path}")
        lines = source_path.read_text(encoding="utf-8").splitlines()
        if len(lines) < 3:
            raise ValueError("Historical dataset must contain header, separator and rows")
        spans = [match.span() for match in re.finditer(r"-+", lines[1])]
        names = [lines[0][start:end].strip() for start, end in spans]
        required = {GROUP_COLUMN, "Performance", "Estado", "errorCount", "successCount", *FEATURES}
        missing = sorted(required - set(names))
        if missing:
            raise ValueError(f"Historical dataset is missing columns: {', '.join(missing)}")
        parsed: list[dict[str, str]] = []
        for line in lines[2:]:
            if not line.strip():
                continue
            parsed.append(
                {
                    name: ("" if line[start:end].strip().upper() == "NULL" else line[start:end].strip())
                    for name, (start, end) in zip(names, spans, strict=True)
                }
            )
        return parsed

    @staticmethod
    def _pipeline(classifier: Any) -> Pipeline:
        encoder = ColumnTransformer(
            [("configuration", OneHotEncoder(handle_unknown="ignore"), [0, 1, 2])]
        )
        return Pipeline([("preprocessor", encoder), ("classifier", classifier)])

    def candidates(self) -> dict[str, Pipeline]:
        return {
            "majority_baseline": self._pipeline(
                DummyClassifier(strategy="most_frequent")
            ),
            "logistic_regression": self._pipeline(
                LogisticRegression(class_weight="balanced", max_iter=2000, random_state=42)
            ),
            "decision_tree": self._pipeline(
                DecisionTreeClassifier(max_depth=5, class_weight="balanced", random_state=42)
            ),
            "random_forest": self._pipeline(
                RandomForestClassifier(
                    n_estimators=250,
                    max_depth=8,
                    min_samples_leaf=3,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                )
            ),
        }

    @staticmethod
    def _split(labels: list[str], groups: list[str]) -> tuple[list[int], list[int]]:
        indexes = list(range(len(labels)))
        for seed in range(RANDOM_STATE, RANDOM_STATE + 100):
            splitter = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=seed)
            train, test = next(splitter.split(indexes, labels, groups))
            train_i, test_i = train.tolist(), test.tolist()
            if set(labels[i] for i in train_i) == {APPLIES, NOT_APPLIES} and set(
                labels[i] for i in test_i
            ) == {APPLIES, NOT_APPLIES}:
                return train_i, test_i
        raise ValueError("Could not create a grouped holdout with both classes")

    @staticmethod
    def _probabilities(model: Pipeline, values: list[list[str]]) -> list[float]:
        classes = list(model.classes_)
        if NOT_APPLIES not in classes:
            return [1.0 if classes[0] == NOT_APPLIES else 0.0] * len(values)
        index = classes.index(NOT_APPLIES)
        return [float(row[index]) for row in model.predict_proba(values)]

    @staticmethod
    def _predictions(probabilities: list[float], threshold: float) -> list[str]:
        return [NOT_APPLIES if value >= threshold else APPLIES for value in probabilities]

    @staticmethod
    def _metrics(
        expected: list[str], probabilities: list[float], threshold: float
    ) -> dict[str, object]:
        predicted = ConfigurationTrainingV2._predictions(probabilities, threshold)
        binary = [1 if value == NOT_APPLIES else 0 for value in expected]
        ranking = sorted(range(len(probabilities)), key=probabilities.__getitem__, reverse=True)
        k = max(1, round(len(ranking) * 0.30))
        selected = ranking[:k]
        positives = sum(binary)
        captured = sum(binary[index] for index in selected)
        return {
            "threshold": threshold,
            "accuracy": accuracy_score(expected, predicted),
            "not_applies_precision": precision_score(
                expected, predicted, pos_label=NOT_APPLIES, zero_division=0
            ),
            "not_applies_recall": recall_score(
                expected, predicted, pos_label=NOT_APPLIES, zero_division=0
            ),
            "not_applies_f1": f1_score(
                expected, predicted, pos_label=NOT_APPLIES, zero_division=0
            ),
            "macro_f1": f1_score(expected, predicted, average="macro", zero_division=0),
            "roc_auc": roc_auc_score(binary, probabilities) if len(set(binary)) == 2 else None,
            "pr_auc": average_precision_score(binary, probabilities)
            if len(set(binary)) == 2
            else None,
            "prevalence_not_applies": positives / len(binary),
            "recall_at_30": captured / positives if positives else 0.0,
            "precision_at_30": captured / k,
            "top_30_rows": k,
            "confusion_matrix_labels": [NOT_APPLIES, APPLIES],
            "confusion_matrix": confusion_matrix(
                expected, predicted, labels=[NOT_APPLIES, APPLIES]
            ).tolist(),
        }

    @staticmethod
    def _best_threshold(expected: list[str], probabilities: list[float]) -> float:
        scored = []
        for threshold in THRESHOLDS:
            predicted = ConfigurationTrainingV2._predictions(probabilities, threshold)
            scored.append(
                (
                    f1_score(expected, predicted, average="macro", zero_division=0),
                    f1_score(
                        expected,
                        predicted,
                        pos_label=NOT_APPLIES,
                        zero_division=0,
                    ),
                    -abs(threshold - 0.5),
                    threshold,
                )
            )
        return float(max(scored)[-1])

    def _oof(
        self,
        model: Pipeline,
        features: list[list[str]],
        labels: list[str],
        groups: list[str],
    ) -> list[float]:
        unique_groups = len(set(groups))
        folds = min(5, unique_groups)
        if folds < 2:
            raise ValueError("At least two Build_Id groups are required")
        output = [0.0] * len(labels)
        splitter = GroupKFold(n_splits=folds)
        for train, validation in splitter.split(features, labels, groups):
            fitted = model.fit([features[i] for i in train], [labels[i] for i in train])
            values = self._probabilities(fitted, [features[i] for i in validation])
            for index, value in zip(validation, values, strict=True):
                output[int(index)] = value
        return output

    def run(self, source_path: Path, output_dir: Path) -> dict[str, object]:
        rows = self.read_fixed_width(source_path)
        reasons = Counter(eligibility_reason(row) for row in rows)
        usable = [row for row in rows if eligibility_reason(row) == "trainable"]
        if len(usable) < 20:
            raise ValueError("At least 20 trainable executed rows are required")
        labels = [technical_label(row) for row in usable]
        if set(labels) != {APPLIES, NOT_APPLIES}:
            raise ValueError("Both applies and not_applies are required")
        features = [feature_row(row) for row in usable]
        groups = [row[GROUP_COLUMN] for row in usable]
        train_i, holdout_i = self._split(labels, groups)
        x_train = [features[i] for i in train_i]
        y_train = [labels[i] for i in train_i]
        g_train = [groups[i] for i in train_i]
        x_holdout = [features[i] for i in holdout_i]
        y_holdout = [labels[i] for i in holdout_i]

        candidate_reports: dict[str, object] = {}
        fitted: dict[str, Pipeline] = {}
        for name, candidate in self.candidates().items():
            oof_probabilities = self._oof(candidate, x_train, y_train, g_train)
            threshold = self._best_threshold(y_train, oof_probabilities)
            candidate_reports[name] = {
                "selected_threshold_train_oof": threshold,
                "train_oof": self._metrics(y_train, oof_probabilities, threshold),
            }

        selectable = ("logistic_regression", "decision_tree", "random_forest")
        selected = max(
            selectable,
            key=lambda name: (
                candidate_reports[name]["train_oof"]["macro_f1"],
                candidate_reports[name]["train_oof"]["pr_auc"],
            ),
        )

        for name, candidate in self.candidates().items():
            fitted[name] = candidate.fit(x_train, y_train)
            threshold = float(candidate_reports[name]["selected_threshold_train_oof"])
            holdout_probabilities = self._probabilities(fitted[name], x_holdout)
            candidate_reports[name]["holdout"] = self._metrics(
                y_holdout, holdout_probabilities, threshold
            )

        selected_threshold = float(
            candidate_reports[selected]["selected_threshold_train_oof"]
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "pipeline": fitted[selected],
                "model_name": selected,
                "decision_threshold": selected_threshold,
                "features": list(FEATURES),
                "classes": [APPLIES, NOT_APPLIES],
                "abstention_policy": "abstain unless Performance=1 and result evidence is complete",
            },
            output_dir / "configuration_model_v2.joblib",
        )

        report: dict[str, object] = {
            "schema_version": "3.0",
            "experiment": "configuration_only_executed_rows_v2",
            "source": str(source_path),
            "source_rows": len(rows),
            "eligibility_distribution": dict(sorted(reasons.items())),
            "training_rows": len(usable),
            "class_distribution": dict(sorted(Counter(labels).items())),
            "features": list(FEATURES),
            "excluded_variables": [
                "Is_In_Prod",
                "ambiente",
                "Performance",
                "CpruebasCarga",
                "CpruebasAcep",
                "pilar",
                "Tcomponente",
                "Metodo",
            ],
            "split": {
                "method": "GroupShuffleSplit by Build_Id",
                "random_state": RANDOM_STATE,
                "train_rows": len(train_i),
                "holdout_rows": len(holdout_i),
                "train_builds": len({groups[i] for i in train_i}),
                "holdout_builds": len({groups[i] for i in holdout_i}),
                "group_overlap": len(
                    {groups[i] for i in train_i} & {groups[i] for i in holdout_i}
                ),
            },
            "selection_protocol": (
                "Model and threshold selected only with grouped OOF predictions from train; "
                "holdout evaluated once after selection."
            ),
            "selection_metric": "macro_f1; PR-AUC breaks ties",
            "selected_model": selected,
            "selected_threshold": selected_threshold,
            "models": candidate_reports,
            "guardrails": {
                "human_approval_required": True,
                "not_executed": "abstain",
                "incomplete_evidence": "abstain",
                "automatic_release": False,
            },
        }
        (output_dir / "configuration_training_v2.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        with (output_dir / "model_comparison_v2.csv").open(
            "w", encoding="utf-8", newline=""
        ) as target:
            fields = [
                "model",
                "threshold_oof",
                "oof_macro_f1",
                "oof_roc_auc",
                "oof_pr_auc",
                "holdout_macro_f1",
                "holdout_not_applies_f1",
                "holdout_roc_auc",
                "holdout_pr_auc",
                "holdout_recall_at_30",
                "holdout_precision_at_30",
            ]
            writer = csv.DictWriter(target, fieldnames=fields)
            writer.writeheader()
            for name, values in candidate_reports.items():
                oof = values["train_oof"]
                holdout = values["holdout"]
                writer.writerow(
                    {
                        "model": name,
                        "threshold_oof": values["selected_threshold_train_oof"],
                        "oof_macro_f1": oof["macro_f1"],
                        "oof_roc_auc": oof["roc_auc"],
                        "oof_pr_auc": oof["pr_auc"],
                        "holdout_macro_f1": holdout["macro_f1"],
                        "holdout_not_applies_f1": holdout["not_applies_f1"],
                        "holdout_roc_auc": holdout["roc_auc"],
                        "holdout_pr_auc": holdout["pr_auc"],
                        "holdout_recall_at_30": holdout["recall_at_30"],
                        "holdout_precision_at_30": holdout["precision_at_30"],
                    }
                )
        return report
