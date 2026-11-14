import random

import pytest

from performance_decision_engine.infrastructure.configuration_explainability_v2 import (
    percentile_summary,
    permute_feature_by_group,
)


def test_percentile_summary() -> None:
    result = percentile_summary([0.1, 0.2, 0.3])
    assert result["mean"] == pytest.approx(0.2)
    assert result["lower_95"] <= result["mean"] <= result["upper_95"]


def test_group_permutation_changes_only_selected_feature() -> None:
    values = [["low", "low", "low"], ["medium", "low", "low"], ["high", "high", "high"]]
    groups = ["a", "a", "b"]
    result = permute_feature_by_group(values, groups, 0, random.Random(3))
    assert [row[1:] for row in result] == [row[1:] for row in values]


def test_group_permutation_is_reproducible() -> None:
    values = [["low"], ["medium"], ["high"]]
    groups = ["a", "b", "c"]
    first = permute_feature_by_group(values, groups, 0, random.Random(42))
    second = permute_feature_by_group(values, groups, 0, random.Random(42))
    assert first == second


def test_empty_summary_fails() -> None:
    with pytest.raises(ValueError):
        percentile_summary([])
