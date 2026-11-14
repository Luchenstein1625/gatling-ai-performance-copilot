import pytest

from performance_decision_engine.infrastructure.configuration_stability_v2 import (
    grouped_bootstrap_indexes,
    percentile_interval,
)


def test_percentile_interval_is_ordered() -> None:
    result = percentile_interval([1.0, 2.0, 3.0, 4.0])
    assert result["lower"] <= result["median"] <= result["upper"]
    assert result["mean"] == pytest.approx(2.5)


def test_grouped_bootstrap_preserves_whole_groups() -> None:
    groups = ["a", "a", "b", "b", "b", "c"]
    samples = grouped_bootstrap_indexes(groups, repetitions=5, seed=42)
    for sample in samples:
        assert len(sample) >= 3
        for name in set(groups[index] for index in sample):
            original = {index for index, group in enumerate(groups) if group == name}
            sampled = {index for index in sample if groups[index] == name}
            assert sampled == original


def test_grouped_bootstrap_is_reproducible() -> None:
    groups = ["a", "a", "b", "c"]
    assert grouped_bootstrap_indexes(groups, 3, 7) == grouped_bootstrap_indexes(groups, 3, 7)


def test_invalid_bootstrap_repetitions_fail() -> None:
    with pytest.raises(ValueError):
        grouped_bootstrap_indexes(["a", "b"], 0)
