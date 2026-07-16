import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from performance_decision_engine.application.use_cases.generate_dataset import (
    GenerateDatasetRow,
)

LABEL_COLUMN = "recommendation_action"
METADATA_COLUMNS = {"schema_version", "metrics_scope"}
CATEGORICAL_COLUMNS = ("load_type", "assertions_all_passed")
MINIMUM_ROWS = 20
TEST_SIZE = 0.25
RANDOM_STATE = 42


class DecisionTreeTrainingBackend:
    """Train a reproducible Decision Tree baseline from the H7 CSV dataset."""

    def train(
        self,
        dataset_path: Path,
        model_path: Path,
        report_path: Path,
    ) -> dict[str, object]:
        rows = self._read_dataset(dataset_path)
        self._validate_rows(rows)

        labels = [row[LABEL_COLUMN] for row in rows]
        feature_columns = [
            name
            for name in GenerateDatasetRow.fieldnames
            if name not in METADATA_COLUMNS and name != LABEL_COLUMN
        ]
        numeric_columns = [name for name in feature_columns if name not in CATEGORICAL_COLUMNS]

        features = [[self._value(row, name) for name in feature_columns] for row in rows]

        class_counts = Counter(labels)
        train_features, test_features, train_labels, test_labels = train_test_split(
            features,
            labels,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=labels,
        )

        numeric_indexes = [feature_columns.index(name) for name in numeric_columns]
        categorical_indexes = [feature_columns.index(name) for name in CATEGORICAL_COLUMNS]

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    Pipeline(
                        steps=[
                            (
                                "imputer",
                                SimpleImputer(strategy="median"),
                            )
                        ]
                    ),
                    numeric_indexes,
                ),
                (
                    "categorical",
                    Pipeline(
                        steps=[
                            (
                                "imputer",
                                SimpleImputer(
                                    strategy="constant",
                                    fill_value="__missing__",
                                ),
                            ),
                            (
                                "encoder",
                                OneHotEncoder(
                                    handle_unknown="ignore",
                                    sparse_output=False,
                                ),
                            ),
                        ]
                    ),
                    categorical_indexes,
                ),
            ],
            remainder="drop",
        )

        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (
                    "classifier",
                    DecisionTreeClassifier(
                        max_depth=4,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        )
        pipeline.fit(train_features, train_labels)
        predictions = pipeline.predict(test_features)

        precision, recall, f1, _ = precision_recall_fscore_support(
            test_labels,
            predictions,
            average="macro",
            zero_division=0,
        )
        classes = sorted(class_counts)
        report: dict[str, object] = {
            "schema_version": "1",
            "model_type": "DecisionTreeClassifier",
            "model_role": "supervised_baseline_approximating_h6",
            "dataset_rows": len(rows),
            "train_rows": len(train_features),
            "test_rows": len(test_features),
            "class_distribution": dict(sorted(class_counts.items())),
            "feature_columns": feature_columns,
            "label_column": LABEL_COLUMN,
            "random_state": RANDOM_STATE,
            "test_size": TEST_SIZE,
            "metrics": {
                "accuracy": accuracy_score(test_labels, predictions),
                "balanced_accuracy": balanced_accuracy_score(
                    test_labels,
                    predictions,
                ),
                "macro_precision": precision,
                "macro_recall": recall,
                "macro_f1": f1,
                "confusion_matrix": confusion_matrix(
                    test_labels,
                    predictions,
                    labels=classes,
                ).tolist(),
                "classification_report": classification_report(
                    test_labels,
                    predictions,
                    labels=classes,
                    output_dict=True,
                    zero_division=0,
                ),
            },
        }

        artifact: dict[str, Any] = {
            "pipeline": pipeline,
            "schema_version": "1",
            "feature_columns": feature_columns,
            "label_column": LABEL_COLUMN,
            "classes": classes,
            "random_state": RANDOM_STATE,
        }

        model_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(artifact, model_path)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return report

    @staticmethod
    def _read_dataset(dataset_path: Path) -> list[dict[str, str]]:
        if not dataset_path.exists():
            raise ValueError(f"Dataset file does not exist: {dataset_path}")

        with dataset_path.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            actual_header = tuple(reader.fieldnames or ())
            expected_header = GenerateDatasetRow.fieldnames
            if actual_header != expected_header:
                raise ValueError("Dataset header is incompatible with H7 schema version 1.")
            return [dict(row) for row in reader]

    @staticmethod
    def _validate_rows(rows: list[dict[str, str]]) -> None:
        if len(rows) < MINIMUM_ROWS:
            raise ValueError(f"At least {MINIMUM_ROWS} dataset rows are required for H8 training.")

        schema_versions = {row["schema_version"] for row in rows}
        if schema_versions != {"1"}:
            raise ValueError("Every dataset row must use schema_version 1.")

        metric_scopes = {row["metrics_scope"] for row in rows}
        if metric_scopes != {"execution"}:
            raise ValueError("Every dataset row must use execution-level metrics.")

        labels = [row[LABEL_COLUMN] for row in rows]
        if any(not label for label in labels):
            raise ValueError("Every dataset row must contain a recommendation label.")

        class_counts = Counter(labels)
        if len(class_counts) < 2:
            raise ValueError("At least two recommendation classes are required.")

        if min(class_counts.values()) < 2:
            raise ValueError(
                "Each recommendation class requires at least two rows " "for stratified evaluation."
            )

    @staticmethod
    def _value(row: dict[str, str], column: str) -> object:
        raw_value = row[column]
        if raw_value == "":
            return None

        if column in CATEGORICAL_COLUMNS:
            return raw_value

        try:
            return float(raw_value)
        except ValueError as exc:
            raise ValueError(f"Column {column!r} must contain numeric values or be empty.") from exc
