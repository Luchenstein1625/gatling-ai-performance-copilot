from performance_decision_engine.infrastructure.model_selection_v3 import (
    APPLIES,
    NOT_APPLIES,
    ModelSelectionV3,
    expand_grid,
)


def test_grid_expansion() -> None:
    values = expand_grid({"a": [1, 2], "b": ["x", "y"]})
    assert len(values) == 4
    assert {item["a"] for item in values} == {1, 2}


def test_search_space_contains_required_models() -> None:
    names = set(ModelSelectionV3.search_space())
    assert names == {
        "logistic_regression",
        "decision_tree",
        "random_forest",
        "hist_gradient_boosting",
    }


def test_cost_counts_are_auditable() -> None:
    expected = [NOT_APPLIES, NOT_APPLIES, APPLIES, APPLIES]
    probabilities = [0.9, 0.1, 0.8, 0.2]
    row = next(item for item in ModelSelectionV3.threshold_rows(expected, probabilities) if item["threshold"] == 0.5)
    assert row["manual_reviews"] == 2
    assert row["false_applies"] == 1
    assert row["applies_reviewed"] == 1
    assert row["total_cost_units"] == 14.0


def test_metrics_include_ranking() -> None:
    expected = [NOT_APPLIES, APPLIES, NOT_APPLIES, APPLIES] * 10
    probabilities = [0.9, 0.1, 0.8, 0.2] * 10
    metrics = ModelSelectionV3.metrics(expected, probabilities)
    assert metrics["roc_auc"] == 1.0
    assert metrics["lift_at_30"] > 1.0
