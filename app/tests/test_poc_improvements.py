import csv
from pathlib import Path

from performance_decision_engine.application.use_cases.analyze_dataset import (
    AnalyzeDataset,
)
from performance_decision_engine.application.use_cases.evaluate_evolution import (
    EvaluateEvolution,
    EvolutionObservation,
    load_evolution_history,
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

    assert set(result["variants"]) == {
        "all_features",
        "without_assertions",
        "operational_core",
    }
    without_assertions = result["variants"]["without_assertions"]
    assert "assertions_failed" in without_assertions["excluded_columns"]
    operational_core = result["variants"]["operational_core"]
    assert "warning_count" in operational_core["excluded_columns"]
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


def _stable_observation(component_id: str, p95: int = 1000) -> EvolutionObservation:
    return EvolutionObservation(
        component_id=component_id,
        recommendation_action="maintain",
        p95_response_time_ms=p95,
        response_time_target_ms=2000,
        error_rate_percent=0,
        assertions_all_passed=True,
    )


def test_stable_component_can_be_recommended_to_evolve() -> None:
    current = Recommendation(action="maintain", explanation="Complies")
    history = [_stable_observation("balances") for _ in range(3)]

    recommendation = EvaluateEvolution().execute("balances", current, history)
    plan = PlanQuadrantAction().execute(recommendation, 5)

    assert recommendation.action == "evolve"
    assert recommendation.evidence["consecutive_successes"] == 4
    assert plan["action"] == "evaluate_load_increase"
    assert plan["proposed_load_increase_percent"] == 10
    assert plan["proposed_quadrant"] == 5
    assert plan["human_validation_required"] is True


def test_component_without_enough_history_remains_unchanged() -> None:
    current = Recommendation(action="maintain", explanation="Complies")

    recommendation = EvaluateEvolution(minimum_consecutive_successes=4).execute(
        "balances",
        current,
        [_stable_observation("balances") for _ in range(2)],
    )

    assert recommendation.action == "maintain"
    assert recommendation.evidence["evolution_reason"] == "insufficient_history"


def test_failure_in_recent_history_prevents_evolution() -> None:
    current = Recommendation(action="maintain", explanation="Complies")
    history = [
        _stable_observation("balances"),
        _stable_observation("balances", p95=1500),
        _stable_observation("balances"),
    ]

    recommendation = EvaluateEvolution().execute("balances", current, history)

    assert recommendation.action == "evolve"


def test_historical_failure_prevents_evolution() -> None:
    current = Recommendation(action="maintain", explanation="Complies")
    history = [
        _stable_observation("balances"),
        EvolutionObservation(
            component_id="balances",
            recommendation_action="review",
            p95_response_time_ms=1100,
            response_time_target_ms=2000,
            error_rate_percent=1.0,
            assertions_all_passed=False,
        ),
    ]

    recommendation = EvaluateEvolution().execute("balances", current, history)

    assert recommendation.action == "maintain"
    assert recommendation.evidence["evolution_reason"] == "historical_failures_detected"


def test_review_recommendation_is_never_overridden() -> None:
    current = Recommendation(action="review", explanation="Failed assertion")

    recommendation = EvaluateEvolution().execute(
        "balances",
        current,
        [_stable_observation("balances") for _ in range(3)],
    )

    assert recommendation is current


def test_evolution_history_csv_is_loaded_and_filtered(tmp_path: Path) -> None:
    history_path = tmp_path / "evolution_history.csv"
    history_path.write_text(
        (
            "component_id,recommendation_action,p95_response_time_ms,"
            "response_time_target_ms,error_rate_percent,assertions_all_passed\n"
            "balances,maintain,1000,2000,0,True\n"
            "offers,maintain,900,2000,0,True\n"
            "balances,maintain,950,2000,0,True\n"
            "balances,maintain,1050,2000,0,True\n"
        ),
        encoding="utf-8",
    )

    history = load_evolution_history(history_path)
    recommendation = EvaluateEvolution().execute(
        "balances",
        Recommendation(action="maintain", explanation="Complies"),
        history,
    )

    assert len(history) == 4
    assert recommendation.action == "evolve"
    assert recommendation.evidence["observed_comparable_executions"] == 3


def test_evolution_history_csv_rejects_missing_columns(tmp_path: Path) -> None:
    history_path = tmp_path / "evolution_history.csv"
    history_path.write_text(
        "component_id,recommendation_action\nbalances,maintain\n",
        encoding="utf-8",
    )

    try:
        load_evolution_history(history_path)
    except ValueError as exc:
        assert "missing required columns" in str(exc)
    else:
        raise AssertionError("Invalid history CSV should be rejected.")
