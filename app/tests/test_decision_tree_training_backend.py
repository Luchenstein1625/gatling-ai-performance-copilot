import csv
import json
from pathlib import Path

import joblib
import pytest

from performance_decision_engine.application.use_cases.generate_dataset import (
    GenerateDatasetRow,
)
from performance_decision_engine.infrastructure.decision_tree_training_backend import (
    DecisionTreeTrainingBackend,
)


def _row(index: int, action: str) -> dict[str, object]:
    review = action == "review"
    return {
        "schema_version": "1",
        "metrics_scope": "execution",
        "load_type": "sequence",
        "enabled_endpoint_count": 1,
        "configured_endpoint_target_count": 1,
        "configured_concurrency_total": 20 + index,
        "configured_iterations_total": 100 + index,
        "strictest_response_time_target_ms": 2000,
        "total_requests": 1000 + index,
        "successful_requests": 990 if review else 1000,
        "failed_requests": 10 if review else 0,
        "error_rate_percent": 1.0 if review else 0.0,
        "min_response_time_ms": 10,
        "mean_response_time_ms": 350 if review else 150,
        "max_response_time_ms": 3000 if review else 800,
        "p50_response_time_ms": 100,
        "p75_response_time_ms": 200,
        "p90_response_time_ms": 900 if review else 400,
        "p95_response_time_ms": 2500 if review else 700,
        "p99_response_time_ms": 2900 if review else 780,
        "requests_per_second": 20.0,
        "assertions_total": 1,
        "assertions_successful": 0 if review else 1,
        "assertions_failed": 1 if review else 0,
        "assertions_all_passed": "False" if review else "True",
        "warning_count": 0,
        "recommendation_action": action,
    }


def _write_dataset(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=GenerateDatasetRow.fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)


def test_trains_and_persists_reproducible_baseline(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.csv"
    model = tmp_path / "model.joblib"
    report = tmp_path / "report.json"
    rows = [_row(index, "maintain" if index % 2 == 0 else "review") for index in range(24)]
    _write_dataset(dataset, rows)

    result = DecisionTreeTrainingBackend().train(dataset, model, report)

    assert result["model_type"] == "DecisionTreeClassifier"
    assert result["dataset_rows"] == 24
    assert model.exists()
    assert report.exists()

    artifact = joblib.load(model)
    assert artifact["schema_version"] == "1"
    assert artifact["label_column"] == "recommendation_action"

    persisted_report = json.loads(report.read_text(encoding="utf-8"))
    assert persisted_report["random_state"] == 42
    assert "macro_f1" in persisted_report["metrics"]


def test_rejects_dataset_with_one_class(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.csv"
    rows = [_row(index, "maintain") for index in range(20)]
    _write_dataset(dataset, rows)

    with pytest.raises(ValueError, match="two recommendation classes"):
        DecisionTreeTrainingBackend().train(
            dataset,
            tmp_path / "model.joblib",
            tmp_path / "report.json",
        )


def test_rejects_dataset_with_too_few_rows(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.csv"
    rows = [_row(index, "maintain" if index % 2 == 0 else "review") for index in range(10)]
    _write_dataset(dataset, rows)

    with pytest.raises(ValueError, match="At least 20"):
        DecisionTreeTrainingBackend().train(
            dataset,
            tmp_path / "model.joblib",
            tmp_path / "report.json",
        )
