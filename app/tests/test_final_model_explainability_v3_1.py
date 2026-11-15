import random

from performance_decision_engine.infrastructure.final_model_explainability_v3_1 import (
    LEVEL_ORDER,
    bootstrap_group_indexes,
    percentile_summary,
    permute_feature_by_group,
)


def test_group_permutation_changes_only_selected_feature() -> None:
    values = [["low", "low", "high"], ["low", "medium", "high"], ["high", "high", "low"]]
    groups = ["a", "a", "b"]
    permuted = permute_feature_by_group(values, groups, 0, random.Random(1))
    assert [row[1:] for row in permuted] == [row[1:] for row in values]


def test_group_bootstrap_preserves_rows_within_each_draw() -> None:
    indexes, groups = bootstrap_group_indexes(["a", "a", "b"], random.Random(2))
    assert len(indexes) == len(groups)
    assert all("#draw_" in group for group in groups)


def test_response_time_order_is_stricter_toward_lower_milliseconds() -> None:
    assert LEVEL_ORDER["ResponseTime"] == ("very_high", "high", "medium", "low")


def test_percentile_summary_has_ordered_interval() -> None:
    summary = percentile_summary([-0.1, 0.0, 0.2, 0.3])
    assert summary["lower_95"] <= summary["mean"] <= summary["upper_95"]

