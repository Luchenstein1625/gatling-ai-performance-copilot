import pytest

from performance_decision_engine.infrastructure.economics_v3 import (
    additional_detections_per_100,
    annual_operating_cost,
    effort_scenario,
)


def test_annual_operating_cost_matches_declared_inputs() -> None:
    assert annual_operating_cost(100, 10, 982) == pytest.approx(1_296_240)


def test_base_scenario_is_auditable() -> None:
    row = effort_scenario("base", 32_256_000, 0.25, 0.50, 1_296_240)
    assert row["gross_benefit_clp"] == pytest.approx(4_032_000)
    assert row["net_benefit_clp"] == pytest.approx(2_735_760)
    assert row["roi"] == pytest.approx(2_735_760 / 1_296_240)


def test_break_even_product_from_inputs() -> None:
    product = annual_operating_cost(100, 10, 982) / 32_256_000
    assert product == pytest.approx(0.040186011904761905)


def test_additional_detections_are_relative_to_prevalence() -> None:
    assert additional_detections_per_100(0.5606, 0.4273) == pytest.approx(13.33)
