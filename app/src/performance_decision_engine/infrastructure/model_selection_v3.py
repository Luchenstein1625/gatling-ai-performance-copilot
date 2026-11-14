"""Final model tuning on frozen train/dev partitions without opening test."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
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
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from performance_decision_engine.infrastructure.configuration_training_v2 import (
    APPLIES,
    FEATURES,
    NOT_APPLIES,
    ConfigurationTrainingV2,
    eligibility_reason,
    feature_row,
    technical_label,
)

RANDOM_STATE = 42
THRESHOLDS = tuple(round(value / 100, 2) for value in range(5, 96, 5))
ERROR_COSTS = {"false_applies": 10.0, "applies_reviewed": 2.0, "manual_review": 1.0}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def expand_grid(grid: dict[str, list[object]]) -> list[dict[str, object]]:
    keys = list(grid)
    return [dict(zip(keys, values, strict=True)) for values in itertools.product(*(grid[k] for k in keys))]


class ModelSelectionV3:
    def __init__(self) -> None:
        self.reader = ConfigurationTrainingV2()

    @staticmethod
    def _pipeline(classifier: Any) -> Pipeline:
        preprocessor = ColumnTransformer(
            [
                (
                    "configuration",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    [0, 1, 2],
                )
            ]
        )
        return Pipeline([("preprocessor", preprocessor), ("classifier", classifier)])

    @staticmethod
    def search_space() -> dict[str, list[dict[str, object]]]:
        return {
            "logistic_regression": expand_grid({"C": [0.1, 1.0, 10.0]}),
            "decision_tree": expand_grid(
                {"max_depth": [3, 5, 8], "min_samples_leaf": [3, 10]}
            ),
            "random_forest": expand_grid(
                {"max_depth": [4, 8, None], "min_samples_leaf": [3, 10]}
            ),
            "hist_gradient_boosting": expand_grid(
                {
                    "learning_rate": [0.03, 0.1],
                    "max_leaf_nodes": [7, 15, 31],
                    "l2_regularization": [0.0, 1.0],
                }
            ),
        }

    def build_model(self, name: str, parameters: dict[str, object]) -> Pipeline:
        if name == "logistic_regression":
            classifier = LogisticRegression(
                C=float(parameters["C"]),
                class_weight="balanced",
                max_iter=2000,
                random_state=RANDOM_STATE,
            )
        elif name == "decision_tree":
            classifier = DecisionTreeClassifier(
                max_depth=int(parameters["max_depth"]),
                min_samples_leaf=int(parameters["min_samples_leaf"]),
                class_weight="balanced",
                random_state=RANDOM_STATE,
            )
        elif name == "random_forest":
            classifier = RandomForestClassifier(
                n_estimators=250,
                max_depth=parameters["max_depth"],
                min_samples_leaf=int(parameters["min_samples_leaf"]),
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            )
        elif name == "hist_gradient_boosting":
            classifier = HistGradientBoostingClassifier(
                learning_rate=float(parameters["learning_rate"]),
                max_leaf_nodes=int(parameters["max_leaf_nodes"]),
                l2_regularization=float(parameters["l2_regularization"]),
                max_iter=200,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            )
        else:
            raise ValueError(f"Unknown model: {name}")
        return self._pipeline(classifier)

    @staticmethod
    def _probabilities(model: Pipeline, values: list[list[str]]) -> list[float]:
        classes = list(model.classes_)
        index = classes.index(NOT_APPLIES)
        return [float(row[index]) for row in model.predict_proba(values)]

    @staticmethod
    def _predictions(probabilities: list[float], threshold: float) -> list[str]:
        return [NOT_APPLIES if value >= threshold else APPLIES for value in probabilities]

    @staticmethod
    def metrics(
        expected: list[str], probabilities: list[float], threshold: float = 0.5
    ) -> dict[str, object]:
        predicted = ModelSelectionV3._predictions(probabilities, threshold)
        binary = [1 if value == NOT_APPLIES else 0 for value in expected]
        ranking = sorted(range(len(probabilities)), key=probabilities.__getitem__, reverse=True)
        count = max(1, round(len(expected) * 0.30))
        selected = ranking[:count]
        positives = sum(binary)
        captured = sum(binary[index] for index in selected)
        prevalence = positives / len(expected)
        precision_at_30 = captured / count
        return {
            "threshold": threshold,
            "accuracy": float(accuracy_score(expected, predicted)),
            "macro_f1": float(f1_score(expected, predicted, average="macro", zero_division=0)),
            "not_applies_f1": float(
                f1_score(expected, predicted, pos_label=NOT_APPLIES, zero_division=0)
            ),
            "not_applies_precision": float(
                precision_score(expected, predicted, pos_label=NOT_APPLIES, zero_division=0)
            ),
            "not_applies_recall": float(
                recall_score(expected, predicted, pos_label=NOT_APPLIES, zero_division=0)
            ),
            "roc_auc": float(roc_auc_score(binary, probabilities)),
            "pr_auc": float(average_precision_score(binary, probabilities)),
            "prevalence_not_applies": prevalence,
            "recall_at_30": captured / positives if positives else 0.0,
            "precision_at_30": precision_at_30,
            "lift_at_30": precision_at_30 / prevalence if prevalence else 0.0,
            "confusion_matrix_labels": [NOT_APPLIES, APPLIES],
            "confusion_matrix": confusion_matrix(
                expected, predicted, labels=[NOT_APPLIES, APPLIES]
            ).tolist(),
        }

    @staticmethod
    def threshold_rows(
        expected: list[str], probabilities: list[float]
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for threshold in THRESHOLDS:
            predicted = ModelSelectionV3._predictions(probabilities, threshold)
            manual_reviews = sum(value == NOT_APPLIES for value in predicted)
            false_applies = sum(
                actual == NOT_APPLIES and prediction == APPLIES
                for actual, prediction in zip(expected, predicted, strict=True)
            )
            applies_reviewed = sum(
                actual == APPLIES and prediction == NOT_APPLIES
                for actual, prediction in zip(expected, predicted, strict=True)
            )
            cost = (
                manual_reviews * ERROR_COSTS["manual_review"]
                + false_applies * ERROR_COSTS["false_applies"]
                + applies_reviewed * ERROR_COSTS["applies_reviewed"]
            )
            metrics = ModelSelectionV3.metrics(expected, probabilities, threshold)
            rows.append(
                {
                    "threshold": threshold,
                    "manual_reviews": manual_reviews,
                    "false_applies": false_applies,
                    "applies_reviewed": applies_reviewed,
                    "total_cost_units": cost,
                    "macro_f1": metrics["macro_f1"],
                    "not_applies_recall": metrics["not_applies_recall"],
                    "not_applies_precision": metrics["not_applies_precision"],
                }
            )
        return rows

    @staticmethod
    def _load_assignments(path: Path) -> dict[str, str]:
        with path.open("r", encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        assignments = {row["build_id_sha256"]: row["partition"] for row in rows}
        if set(assignments.values()) != {"train", "dev", "test"}:
            raise ValueError("Partition assignment file is incomplete")
        return assignments

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
        output_dir: Path,
    ) -> dict[str, object]:
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        if protocol["source_sha256"] != sha256_file(source_path):
            raise ValueError("Dataset SHA-256 does not match frozen protocol")
        if protocol["test_lock"]["opened_for_model_selection"] is not False:
            raise ValueError("Frozen protocol test lock is not intact")
        assignments = self._load_assignments(assignments_path)
        rows = self.reader.read_fixed_width(source_path)
        usable = [row for row in rows if eligibility_reason(row) == "trainable"]
        partitioned: dict[str, list[dict[str, str]]] = {"train": [], "dev": [], "test": []}
        for row in usable:
            partition = assignments.get(sha256_text(row["Build_Id"]))
            if partition is None:
                raise ValueError("Eligible Build_Id is absent from frozen assignments")
            partitioned[partition].append(row)

        x_train = [feature_row(row) for row in partitioned["train"]]
        y_train = [technical_label(row) for row in partitioned["train"]]
        x_dev = [feature_row(row) for row in partitioned["dev"]]
        y_dev = [technical_label(row) for row in partitioned["dev"]]

        tuning_rows: list[dict[str, object]] = []
        trained: dict[tuple[str, int], Pipeline] = {}
        configurations: dict[tuple[str, int], dict[str, object]] = {}
        for model_name, parameter_sets in self.search_space().items():
            for configuration_id, parameters in enumerate(parameter_sets, start=1):
                model = self.build_model(model_name, parameters)
                model.fit(x_train, y_train)
                probabilities = self._probabilities(model, x_dev)
                metrics = self.metrics(y_dev, probabilities)
                key = (model_name, configuration_id)
                trained[key] = model
                configurations[key] = parameters
                tuning_rows.append(
                    {
                        "model": model_name,
                        "configuration_id": configuration_id,
                        "parameters": json.dumps(parameters, sort_keys=True),
                        **{name: metrics[name] for name in (
                            "roc_auc", "pr_auc", "macro_f1", "not_applies_f1",
                            "recall_at_30", "precision_at_30", "lift_at_30"
                        )},
                    }
                )

        best_by_model: dict[str, dict[str, object]] = {}
        for model_name in self.search_space():
            candidates = [row for row in tuning_rows if row["model"] == model_name]
            best_by_model[model_name] = max(
                candidates, key=lambda row: (float(row["roc_auc"]), float(row["macro_f1"]))
            )
        selected_row = max(
            best_by_model.values(),
            key=lambda row: (float(row["roc_auc"]), float(row["macro_f1"])),
        )
        selected_key = (str(selected_row["model"]), int(selected_row["configuration_id"]))
        selected_model = trained[selected_key]
        selected_probabilities = self._probabilities(selected_model, x_dev)
        threshold_analysis = self.threshold_rows(y_dev, selected_probabilities)
        selected_threshold_row = min(
            threshold_analysis,
            key=lambda row: (float(row["total_cost_units"]), -float(row["macro_f1"])),
        )
        selected_threshold = float(selected_threshold_row["threshold"])
        selected_metrics = self.metrics(y_dev, selected_probabilities, selected_threshold)

        # Operational baselines are evaluated on dev only; no test labels are read here.
        prevalence = sum(value == NOT_APPLIES for value in y_dev) / len(y_dev)
        baseline_reports = {
            "B0_random_at_30": {
                "recall_at_30_expected": 0.30,
                "precision_at_30_expected": prevalence,
                "lift_at_30_expected": 1.0,
            },
            "B1_majority_applies": {
                "macro_f1": float(
                    f1_score(y_dev, [APPLIES] * len(y_dev), average="macro", zero_division=0)
                ),
                "roc_auc": 0.5,
                "pr_auc": prevalence,
            },
            "B2_current_QA_heuristic": {
                "status": "pending_formalization_with_QA_analysts"
            },
            "B3_context_history": {
                "status": "not_applicable_context_variables_excluded_by_scope"
            },
        }

        output_dir.mkdir(parents=True, exist_ok=True)
        self._write_csv(output_dir / "tuning_results_dev_v3.csv", tuning_rows)
        self._write_csv(
            output_dir / "best_model_comparison_dev_v3.csv",
            list(best_by_model.values()),
        )
        self._write_csv(output_dir / "threshold_analysis_dev_v3.csv", threshold_analysis)
        joblib.dump(
            {
                "pipeline": selected_model,
                "model_name": selected_key[0],
                "parameters": configurations[selected_key],
                "decision_threshold_dev": selected_threshold,
                "features": list(FEATURES),
                "status": "candidate_selected_on_dev_test_not_opened",
            },
            output_dir / "selected_candidate_dev_v3.joblib",
        )
        report: dict[str, object] = {
            "schema_version": "3.0",
            "experiment": "final_model_selection_train_dev_only",
            "source_sha256": protocol["source_sha256"],
            "protocol_version": protocol["protocol_version"],
            "features": list(FEATURES),
            "rows": {
                "train_used": len(x_train),
                "dev_used": len(x_dev),
                "test_reserved_not_evaluated": len(partitioned["test"]),
            },
            "test_status": "LOCKED_NOT_EVALUATED",
            "selection_rule": "highest dev ROC-AUC; dev macro-F1 breaks ties",
            "search_space": self.search_space(),
            "best_by_model": best_by_model,
            "selected_model": selected_key[0],
            "selected_configuration_id": selected_key[1],
            "selected_parameters": configurations[selected_key],
            "selected_threshold_dev_by_cost": selected_threshold,
            "selected_threshold_cost_row": selected_threshold_row,
            "selected_dev_metrics_at_cost_threshold": selected_metrics,
            "cost_policy": ERROR_COSTS,
            "baselines": baseline_reports,
            "next_gate": (
                "Calibrate selected candidate using train predictions and dev only; do not "
                "open test until model-final tag exists."
            ),
        }
        (output_dir / "model_selection_dev_v3.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report
