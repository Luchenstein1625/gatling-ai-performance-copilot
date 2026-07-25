import csv
import json
from collections import Counter
from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from performance_decision_engine.application.use_cases.generate_dataset import (
    GenerateDatasetRow,
)
from performance_decision_engine.infrastructure.decision_tree_training_backend import (
    CATEGORICAL_COLUMNS,
    LABEL_COLUMN,
    METADATA_COLUMNS,
    MINIMUM_ROWS,
)

ASSERTION_COLUMNS = {
    "assertions_total",
    "assertions_successful",
    "assertions_failed",
    "assertions_all_passed",
}


class ModelEvaluator:
    """Compare the H8 baseline with an assertion-free ablation experiment."""

    def evaluate(
        self,
        dataset_path: Path,
        output_path: Path,
        *,
        seeds: int = 10,
    ) -> dict[str, object]:
        if seeds < 2:
            raise ValueError("At least two evaluation seeds are required.")
        rows = self._read_rows(dataset_path)
        labels = [row[LABEL_COLUMN] for row in rows]
        class_counts = Counter(labels)
        if len(rows) < MINIMUM_ROWS or len(class_counts) < 2 or min(class_counts.values()) < 2:
            raise ValueError("Dataset does not meet the H8 minimum evaluation safeguards.")

        all_features = [
            name
            for name in GenerateDatasetRow.fieldnames
            if name not in METADATA_COLUMNS and name != LABEL_COLUMN
        ]
        variants = {
            "all_features": all_features,
            "without_assertions": [name for name in all_features if name not in ASSERTION_COLUMNS],
        }
        results = {
            name: self._evaluate_variant(
                rows,
                labels,
                [
                    column
                    for column in columns
                    if not all(row[column].strip() == "" for row in rows)
                ],
                seeds,
            )
            for name, columns in variants.items()
        }
        majority_accuracy = max(class_counts.values()) / len(rows)
        payload: dict[str, object] = {
            "schema_version": "1",
            "dataset_rows": len(rows),
            "class_distribution": dict(sorted(class_counts.items())),
            "evaluation": "repeated_stratified_holdout",
            "seeds": seeds,
            "test_size": 0.25,
            "majority_baseline_accuracy": majority_accuracy,
            "variants": results,
            "interpretation": (
                "Compare without_assertions against all_features to quantify how much "
                "assertion-derived variables influence the reported performance."
            ),
            "limitations": [
                "Small datasets produce high metric variability.",
                "Rows are not grouped by microservice because H7 schema version 1 has no group id.",
            ],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    @staticmethod
    def _read_rows(dataset_path: Path) -> list[dict[str, str]]:
        with dataset_path.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            if tuple(reader.fieldnames or ()) != GenerateDatasetRow.fieldnames:
                raise ValueError("Dataset header is incompatible with H7 schema version 1.")
            return [dict(row) for row in reader]

    def _evaluate_variant(
        self,
        rows: list[dict[str, str]],
        labels: list[str],
        columns: list[str],
        seeds: int,
    ) -> dict[str, object]:
        features = [[self._value(row, name) for name in columns] for row in rows]
        categorical = [name for name in columns if name in CATEGORICAL_COLUMNS]
        numeric = [name for name in columns if name not in CATEGORICAL_COLUMNS]
        categorical_indexes = [columns.index(name) for name in categorical]
        numeric_indexes = [columns.index(name) for name in numeric]
        splitter = StratifiedShuffleSplit(n_splits=seeds, test_size=0.25, random_state=42)
        metrics: list[dict[str, float]] = []

        for train_indexes, test_indexes in splitter.split(features, labels):
            pipeline = self._pipeline(numeric_indexes, categorical_indexes)
            train_x = [features[index] for index in train_indexes]
            test_x = [features[index] for index in test_indexes]
            train_y = [labels[index] for index in train_indexes]
            test_y = [labels[index] for index in test_indexes]
            pipeline.fit(train_x, train_y)
            predictions = pipeline.predict(test_x)
            metrics.append(
                {
                    "accuracy": float(accuracy_score(test_y, predictions)),
                    "balanced_accuracy": float(balanced_accuracy_score(test_y, predictions)),
                    "macro_f1": float(f1_score(test_y, predictions, average="macro")),
                    "review_f1": float(
                        f1_score(
                            test_y,
                            predictions,
                            labels=["review"],
                            average="macro",
                            zero_division=0,
                        )
                    ),
                }
            )

        return {
            "feature_columns": columns,
            "excluded_columns": sorted(
                set(GenerateDatasetRow.fieldnames).difference(columns)
                - METADATA_COLUMNS
                - {LABEL_COLUMN}
            ),
            "metrics": {
                metric: self._summary([result[metric] for result in metrics])
                for metric in metrics[0]
            },
        }

    @staticmethod
    def _pipeline(
        numeric_indexes: list[int],
        categorical_indexes: list[int],
    ) -> Pipeline:
        transformers: list[tuple[str, object, list[int]]] = []
        if numeric_indexes:
            transformers.append(
                (
                    "numeric",
                    Pipeline([("imputer", SimpleImputer(strategy="median"))]),
                    numeric_indexes,
                )
            )
        if categorical_indexes:
            transformers.append(
                (
                    "categorical",
                    Pipeline(
                        [
                            (
                                "imputer",
                                SimpleImputer(strategy="constant", fill_value="__missing__"),
                            ),
                            (
                                "encoder",
                                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                            ),
                        ]
                    ),
                    categorical_indexes,
                )
            )
        return Pipeline(
            [
                ("preprocessor", ColumnTransformer(transformers)),
                (
                    "classifier",
                    DecisionTreeClassifier(
                        max_depth=4,
                        class_weight="balanced",
                        random_state=42,
                    ),
                ),
            ]
        )

    @staticmethod
    def _summary(values: list[float]) -> dict[str, float]:
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        return {"mean": mean, "std": variance**0.5, "min": min(values), "max": max(values)}

    @staticmethod
    def _value(row: dict[str, str], column: str) -> object:
        value = row[column]
        if value == "":
            return None
        if column in CATEGORICAL_COLUMNS:
            return value
        return float(value)
