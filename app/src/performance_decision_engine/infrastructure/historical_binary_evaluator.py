import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_graphviz, export_text

RANDOM_STATE = 42
TEST_SIZE = 0.25
GROUP_COLUMN = "Build_Id"
POSITIVE_CLASS = "review"
CLASSES = ("review", "maintain", "upgrade")

# Deliberately excludes post-result and business-decision columns that disclose the target.
NUMERIC_FEATURES = (
    "CpruebasCarga",
    "CpruebasAcep",
    "Is_In_Prod",
)
CATEGORICAL_FEATURES = (
    "pilar",
    "Tcomponente",
    "Metodo",
    "Concurrency",
    "Iterations",
    "ResponseTime",
    "ambiente",
)
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
MODEL_NAMES = ("decision_tree", "logistic_regression", "random_forest")


class HistoricalBinaryEvaluator:
    """Recommend review/maintain/upgrade from historical Gatling executions."""

    def evaluate(self, source_path: Path, output_dir: Path) -> dict[str, object]:
        rows = self.read_fixed_width(source_path)
        usable = [row for row in rows if self._has_required_result(row)]
        if len(usable) < 20:
            raise ValueError("At least 20 labeled historical rows are required.")

        labels = [self._label(row) for row in usable]
        if len(set(labels)) < 2:
            raise ValueError("At least two recommendation classes are required.")

        features = [[self._value(row, name) for name in FEATURES] for row in usable]
        groups = [row.get(GROUP_COLUMN) or f"row-{index}" for index, row in enumerate(usable)]
        train_indexes, test_indexes = self._group_split(labels, groups)
        x_train = [features[index] for index in train_indexes]
        x_test = [features[index] for index in test_indexes]
        y_train = [labels[index] for index in train_indexes]
        y_test = [labels[index] for index in test_indexes]

        candidates = self._candidates()
        reports: dict[str, dict[str, object]] = {}
        fitted: dict[str, Pipeline] = {}
        for name, pipeline in candidates.items():
            pipeline.fit(x_train, y_train)
            fitted[name] = pipeline
            reports[name] = {
                "train": self._metrics(y_train, list(pipeline.predict(x_train))),
                "test": self._metrics(y_test, list(pipeline.predict(x_test))),
            }

        selected_name = max(
            MODEL_NAMES,
            key=lambda name: (
                float(reports[name]["test"]["review_f1"]),
                float(reports[name]["test"]["review_recall"]),
            ),
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "pipeline": fitted[selected_name],
                "model_name": selected_name,
                "features": list(FEATURES),
                "positive_class": POSITIVE_CLASS,
                "random_state": RANDOM_STATE,
            },
            output_dir / "historical_recommendation_model.joblib",
        )
        self._write_normalized_dataset(usable, output_dir / "historical_recommendation_dataset.csv")
        self._export_tree(fitted["decision_tree"], output_dir)

        report: dict[str, object] = {
            "problem_type": "multiclass_recommendation",
            "target": "review_maintain_upgrade",
            "positive_class": POSITIVE_CLASS,
            "source_rows": len(rows),
            "labeled_rows": len(usable),
            "discarded_unlabeled_rows": len(rows) - len(usable),
            "class_distribution": dict(sorted(Counter(labels).items())),
            "split": {
                "method": "group_holdout_by_build_id",
                "test_size": TEST_SIZE,
                "random_state": RANDOM_STATE,
                "train_rows": len(train_indexes),
                "test_rows": len(test_indexes),
                "train_groups": len({groups[index] for index in train_indexes}),
                "test_groups": len({groups[index] for index in test_indexes}),
                "group_overlap": 0,
            },
            "features": list(FEATURES),
            "label_policy": {
                "review": (
                    "Any failed/irregular/incomplete execution; never downgrades automatically."
                ),
                "maintain": (
                    "Execution passes and the current configuration measures what is needed."
                ),
                "upgrade": (
                    "Execution passes stably with enough headroom to evaluate a higher quadrant."
                ),
                "downgrade": "Excluded: it is only a human decision after review.",
            },
            "excluded_target_proxies": [
                "Performance",
                "Estado",
                "ReasonTag",
                "Reason_Detail",
                "rating",
                "EndpointSwagger",
                "simulation",
                "maxUsers",
                "duration",
                "Conteo",
                "successCount",
                "errorCount",
                "min/p50/p90/p95/p99/max/avg/stddev/rps",
            ],
            "models": reports,
            "selection_rule": "highest test F1 for review; recall breaks ties",
            "selected_model": selected_name,
            "limitations": [
                "Historical labels are operational records and must be audited for consistency.",
                "The holdout is grouped by Build_Id to prevent scenarios from the same "
                "build leaking across partitions.",
                "Upgrade is a proposal for human validation, not an autonomous quadrant change.",
                "Review always preserves the current quadrant until a specialist "
                "diagnoses the failure.",
            ],
        }
        (output_dir / "historical_recommendation_evaluation.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report

    @staticmethod
    def read_fixed_width(source_path: Path) -> list[dict[str, str]]:
        if not source_path.exists():
            raise ValueError(f"Historical dataset does not exist: {source_path}")
        lines = source_path.read_text(encoding="utf-8").splitlines()
        if len(lines) < 3:
            raise ValueError("Historical dataset must contain header, separator and data rows.")
        spans = [match.span() for match in re.finditer(r"-+", lines[1])]
        names = [lines[0][start:end].strip() for start, end in spans]
        if GROUP_COLUMN not in names:
            raise ValueError("Historical dataset header is incompatible.")
        parsed: list[dict[str, str]] = []
        for line in lines[2:]:
            if not line.strip():
                continue
            parsed.append(
                {
                    name: HistoricalBinaryEvaluator._clean(line[start:end].strip())
                    for name, (start, end) in zip(names, spans, strict=True)
                }
            )
        return parsed

    @staticmethod
    def _clean(value: str) -> str:
        return "" if value.upper() == "NULL" else value

    @staticmethod
    def _label(row: dict[str, str]) -> str:
        """Create an auditable expert-policy label from post-execution evidence."""
        performance_ok = row.get("Performance") == "1"
        status_ok = row.get("Estado", "").strip().lower() == "success"
        errors = HistoricalBinaryEvaluator._number(row.get("errorCount"))
        successes = HistoricalBinaryEvaluator._number(row.get("successCount"))
        p95 = HistoricalBinaryEvaluator._number(row.get("p95"))
        if not performance_ok or not status_ok or errors is None or errors > 0:
            return "review"
        if successes is None or successes <= 0 or p95 is None:
            return "review"
        # Conservative headroom rule based only on reliable numeric fields in this export.
        if p95 <= 1500:
            return "upgrade"
        return "maintain"

    @staticmethod
    def _has_required_result(row: dict[str, str]) -> bool:
        return bool(row.get("Build_Id") and row.get("Performance") in {"0", "1"})

    @staticmethod
    def _number(value: str | None) -> float | None:
        try:
            return float(value) if value not in {None, ""} else None
        except ValueError:
            return None

    @staticmethod
    def _value(row: dict[str, str], name: str) -> object:
        value = row.get(name, "")
        if name in CATEGORICAL_FEATURES:
            return value or None
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _group_split(labels: list[str], groups: list[str]) -> tuple[list[int], list[int]]:
        indexes = list(range(len(labels)))
        for seed in range(RANDOM_STATE, RANDOM_STATE + 100):
            splitter = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=seed)
            train, test = next(splitter.split(indexes, labels, groups))
            train_indexes, test_indexes = train.tolist(), test.tolist()
            all_classes = set(labels)
            if (
                set(labels[index] for index in train_indexes) == all_classes
                and set(labels[index] for index in test_indexes) == all_classes
            ):
                return train_indexes, test_indexes
        raise ValueError("Could not create a grouped holdout containing both classes.")

    @staticmethod
    def _preprocessor(*, scale_numeric: bool = False) -> ColumnTransformer:
        numeric_steps: list[tuple[str, Any]] = [("imputer", SimpleImputer(strategy="median"))]
        if scale_numeric:
            numeric_steps.append(("scaler", StandardScaler()))
        return ColumnTransformer(
            [
                ("numeric", Pipeline(numeric_steps), list(range(len(NUMERIC_FEATURES)))),
                (
                    "categorical",
                    Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            (
                                "encoder",
                                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                            ),
                        ]
                    ),
                    list(range(len(NUMERIC_FEATURES), len(FEATURES))),
                ),
            ]
        )

    def _candidates(self) -> dict[str, Pipeline]:
        return {
            "decision_tree": Pipeline(
                [
                    ("preprocessor", self._preprocessor()),
                    (
                        "classifier",
                        DecisionTreeClassifier(
                            max_depth=5, class_weight="balanced", random_state=RANDOM_STATE
                        ),
                    ),
                ]
            ),
            "logistic_regression": Pipeline(
                [
                    ("preprocessor", self._preprocessor(scale_numeric=True)),
                    (
                        "classifier",
                        LogisticRegression(
                            class_weight="balanced", max_iter=2000, random_state=RANDOM_STATE
                        ),
                    ),
                ]
            ),
            "random_forest": Pipeline(
                [
                    ("preprocessor", self._preprocessor()),
                    (
                        "classifier",
                        RandomForestClassifier(
                            n_estimators=250,
                            max_depth=8,
                            min_samples_leaf=3,
                            class_weight="balanced",
                            random_state=RANDOM_STATE,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
        }

    @staticmethod
    def _metrics(expected: list[str], predicted: list[str]) -> dict[str, object]:
        labels = [name for name in CLASSES if name in set(expected) | set(predicted)]
        return {
            "accuracy": accuracy_score(expected, predicted),
            "review_precision": precision_score(
                expected, predicted, labels=[POSITIVE_CLASS], average=None, zero_division=0
            )[0],
            "review_recall": recall_score(
                expected, predicted, labels=[POSITIVE_CLASS], average=None, zero_division=0
            )[0],
            "review_f1": f1_score(
                expected, predicted, labels=[POSITIVE_CLASS], average=None, zero_division=0
            )[0],
            "confusion_matrix_labels": labels,
            "confusion_matrix": confusion_matrix(expected, predicted, labels=labels).tolist(),
            "classification_report": classification_report(
                expected, predicted, labels=labels, output_dict=True, zero_division=0
            ),
        }

    @staticmethod
    def _export_tree(pipeline: Pipeline, output_dir: Path) -> None:
        preprocessor = pipeline.named_steps["preprocessor"]
        classifier = pipeline.named_steps["classifier"]
        names = [str(name) for name in preprocessor.get_feature_names_out()]
        (output_dir / "decision_tree_rules.txt").write_text(
            export_text(classifier, feature_names=names), encoding="utf-8"
        )
        export_graphviz(
            classifier,
            out_file=str(output_dir / "decision_tree.dot"),
            feature_names=names,
            class_names=[str(name) for name in classifier.classes_],
            filled=True,
            rounded=True,
            special_characters=False,
        )

    @staticmethod
    def _write_normalized_dataset(rows: list[dict[str, str]], output_path: Path) -> None:
        fieldnames = ["recommendation_action", GROUP_COLUMN, *FEATURES]
        with output_path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        "recommendation_action": HistoricalBinaryEvaluator._label(row),
                        GROUP_COLUMN: row.get(GROUP_COLUMN, ""),
                        **{name: row.get(name, "") for name in FEATURES},
                    }
                )
