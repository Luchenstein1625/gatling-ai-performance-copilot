import csv
from collections import Counter
from pathlib import Path

from performance_decision_engine.application.use_cases.generate_dataset import (
    GenerateDatasetRow,
)


class AnalyzeDataset:
    """Produce a reproducible quality report for one H7 dataset."""

    def execute(self, dataset_path: Path) -> dict[str, object]:
        if not dataset_path.exists():
            raise ValueError(f"Dataset file does not exist: {dataset_path}")

        with dataset_path.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            header = tuple(reader.fieldnames or ())
            if header != GenerateDatasetRow.fieldnames:
                raise ValueError("Dataset header is incompatible with H7 schema version 1.")
            rows = [dict(row) for row in reader]

        if not rows:
            raise ValueError("Dataset does not contain data rows.")

        missing_by_column = {
            column: sum(row[column].strip() == "" for row in rows) for column in header
        }
        completely_empty = [
            column for column, count in missing_by_column.items() if count == len(rows)
        ]
        duplicate_rows = len(rows) - len({tuple(row[column] for column in header) for row in rows})
        labels = Counter(row["recommendation_action"] for row in rows)

        return {
            "schema_version": "1",
            "dataset": str(dataset_path),
            "rows": len(rows),
            "columns": len(header),
            "class_distribution": dict(sorted(labels.items())),
            "duplicate_rows": duplicate_rows,
            "completely_empty_columns": completely_empty,
            "missing_values_by_column": missing_by_column,
            "warnings": [
                message
                for condition, message in (
                    (
                        bool(completely_empty),
                        (
                            "One or more columns are completely empty and cannot "
                            "contribute to training."
                        ),
                    ),
                    (
                        duplicate_rows > 0,
                        "Duplicate rows can make evaluation metrics overly optimistic.",
                    ),
                    (
                        len(labels) < 2,
                        "At least two classes are required for supervised evaluation.",
                    ),
                )
                if condition
            ],
        }
