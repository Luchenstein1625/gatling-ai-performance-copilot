import csv
from pathlib import Path

from performance_decision_engine.application.use_cases.analyze_dataset import (
    AnalyzeDataset,
)
from performance_decision_engine.application.use_cases.generate_dataset import (
    GenerateDatasetRow,
)
from performance_decision_engine.application.use_cases.plan_quadrant_action import (
    PlanQuadrantAction,
)
from performance_decision_engine.domain.entities.recommendation import Recommendation
from performance_decision_engine.infrastructure.model_evaluator import ModelEvaluator


def _row(index: int, action: str) -> dict[str, object]:
    review = action == "review"
    row = {name: 1 for name in GenerateDatasetRow.fieldnames}
    row.update(
        {
            "schema_version": "1",
            "metrics_scope": "execution",
            "load_type": "sequence",
            "p75_response_time_ms": "",
            "failed_requests": 1 if review else 0,
            "error_rate_percent": 1.0 if review else 0.0,
            "mean_response_time_ms": 300 + index if review else 100 + index,
            "assertions_total": 1,
            "assertions_successful": 0 if review else 1,
            "assertions_failed": 1 if review else 0,
            "assertions_all_passed": "False" if review else "True",
            "recommendation_action": action,
        }
    )
    return row


def _dataset(path: Path) -> None:
    rows = [_row(index, "maintain" if index % 2 == 0 else "review") for index in range(24)]
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=GenerateDatasetRow.fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_dataset_quality_names_empty_columns(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.csv"
    _dataset(dataset)

    result = AnalyzeDataset().execute(dataset)

    assert result["rows"] == 24
    assert result["completely_empty_columns"] == ["p75_response_time_ms"]
    assert result["class_distribution"] == {"maintain": 12, "review": 12}


def test_model_evaluation_compares_assertion_ablation(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.csv"
    output = tmp_path / "evaluation.json"
    _dataset(dataset)

    result = ModelEvaluator().evaluate(dataset, output, seeds=2)

    assert set(result["variants"]) == {"all_features", "without_assertions"}
    without_assertions = result["variants"]["without_assertions"]
    assert "assertions_failed" in without_assertions["excluded_columns"]
    assert output.exists()


def test_review_plan_keeps_quadrant_until_human_validation() -> None:
    recommendation = Recommendation(
        action="review",
        explanation="Failed assertion",
        evidence={"triggered_rule": "assertions"},
    )

    result = PlanQuadrantAction().execute(recommendation, 5)

    assert result["action"] == "review_configuration"
    assert result["proposed_quadrant"] == 5
    assert result["human_validation_required"] is True
