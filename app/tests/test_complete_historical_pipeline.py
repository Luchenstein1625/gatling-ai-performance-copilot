from pathlib import Path

from performance_decision_engine.infrastructure.complete_historical_pipeline import (
    CompleteHistoricalPipeline,
)
from test_historical_binary_evaluator import _dataset


def test_complete_pipeline_implements_four_layers(tmp_path: Path) -> None:
    source = tmp_path / "historical.txt"
    output = tmp_path / "complete"
    _dataset(source, count=60)

    report = CompleteHistoricalPipeline().evaluate_complete(source, output)

    assert set(report["layers"]) == {
        "1_applicability",
        "2_decision",
        "3_optimization",
        "4_evaluation",
    }
    assert set(report["layers"]["1_applicability"]["models"]) == {
        "decision_tree",
        "logistic_regression",
        "random_forest",
        "majority_baseline",
    }
    assert report["layers"]["4_evaluation"]["group_overlap"] == 0
    assert report["layers"]["4_evaluation"]["review_configuration_change_violations"] == 0
    assert report["layers"]["4_evaluation"]["future_validation_status"] == "pending_new_execution"
    assert (output / "complete_pipeline_evaluation.json").exists()
    assert (output / "layered_recommendations.csv").exists()
    assert (output / "layer1_applicability_model.joblib").exists()


def test_review_never_changes_configuration() -> None:
    pipeline = CompleteHistoricalPipeline()
    row = {
        "Build_Id": "1",
        "Performance": "0",
        "Estado": "Failed",
        "errorCount": "3",
        "successCount": "0",
        "p95": "",
        "Concurrency": "high",
        "Iterations": "medium",
        "ResponseTime": "high",
        "pilar": "OSS",
        "Tcomponente": "Backend",
        "Metodo": "GET",
    }

    result = pipeline._recommend(row, "not_applies", {})

    assert result["action"] == "review"
    assert result["proposed_parameters"] == result["current_parameters"]
    assert result["proposed_quadrant"] == result["current_quadrant"]


def test_upgrade_is_limited_to_one_level() -> None:
    assert CompleteHistoricalPipeline._one_step_higher("low", "very_high") == "medium"
    assert CompleteHistoricalPipeline._one_step_higher("very_high", "very_high") == "very_high"


def test_layer_four_validates_a_real_reexecution() -> None:
    proposal = {
        "action": "upgrade",
        "proposed_parameters": {"Concurrency": "high"},
    }
    new_result = {
        "Estado": "Success",
        "errorCount": "0",
        "successCount": "800",
        "p95": "1400",
        "rps": "15.2",
    }

    validation = CompleteHistoricalPipeline.validate_reexecution(proposal, new_result)

    assert validation["status"] == "validated"
    assert validation["approved"] is True


def test_failed_reexecution_returns_to_review() -> None:
    proposal = {"action": "upgrade", "proposed_parameters": {"Concurrency": "high"}}
    new_result = {
        "Estado": "Failed",
        "errorCount": "2",
        "successCount": "798",
        "p95": "2200",
    }

    validation = CompleteHistoricalPipeline.validate_reexecution(proposal, new_result)

    assert validation["status"] == "review"
    assert validation["approved"] is False
