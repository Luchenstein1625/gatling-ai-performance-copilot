import pytest

from performance_decision_engine.infrastructure.economics_anchored_v3_1 import (
    anchored_reduction,
    anchored_scenario,
    break_even_reduction,
    required_annual_records,
)


ANNUAL_BUDGET = 32_256_000
ANNUAL_COST = 1_296_240
ADDITIONAL = 13.33333333333333


def test_negative_detection_difference_has_zero_benefit_floor() -> None:
    assert anchored_reduction(-4.75, 2.0) == 0.0


@pytest.mark.parametrize(
    ("k", "expected_net"),
    [(0.5, -758_640), (1.0, -221_040), (2.0, 854_160)],
)
def test_control_scenarios_match_preregistered_values(k: float, expected_net: float) -> None:
    row = anchored_scenario(ANNUAL_BUDGET, ANNUAL_COST, 0.25, ADDITIONAL, k)
    assert row["net_benefit_point_clp"] == pytest.approx(expected_net)


def test_break_even_at_25_percent_coverage_requires_16_percent_reduction() -> None:
    assert break_even_reduction(ANNUAL_COST, ANNUAL_BUDGET, 0.25) == pytest.approx(0.16074404761904762)


def test_required_records_uses_incremental_detection_rate() -> None:
    expected = ANNUAL_COST / (224_000 * 0.30 * ADDITIONAL / 100)
    assert required_annual_records(ANNUAL_COST, 224_000, ADDITIONAL) == pytest.approx(expected)

