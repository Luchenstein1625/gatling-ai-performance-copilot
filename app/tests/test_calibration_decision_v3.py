import pytest

from performance_decision_engine.infrastructure.calibration_decision_v3 import (
    expected_calibration_error,
    percentile_interval,
    wilson_interval,
)


def test_wilson_interval_contains_estimate() -> None:
    interval = wilson_interval(1, 21)
    assert interval["lower"] <= interval["estimate"] <= interval["upper"]


def test_wilson_empty_total() -> None:
    interval = wilson_interval(0, 0)
    assert interval["estimate"] is None


def test_ece_is_zero_for_matching_bins() -> None:
    error, rows = expected_calibration_error([0, 0, 1, 1], [0.0, 0.0, 1.0, 1.0], bins=2)
    assert error == pytest.approx(0.0)
    assert sum(row["rows"] for row in rows) == 4


def test_percentile_interval() -> None:
    result = percentile_interval([-1.0, 0.0, 1.0])
    assert result["lower_95"] <= 0 <= result["upper_95"]
