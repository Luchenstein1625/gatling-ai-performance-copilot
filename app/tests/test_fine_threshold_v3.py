import pytest

from performance_decision_engine.infrastructure.configuration_training_v2 import APPLIES, NOT_APPLIES
from performance_decision_engine.infrastructure.fine_threshold_v3 import (
    FINE_THRESHOLDS,
    automatic_release_gate,
    policy_counts,
)


def test_grid_includes_review_all_and_previous_boundary() -> None:
    assert FINE_THRESHOLDS[0] == 0.0
    assert 0.05 in FINE_THRESHOLDS
    assert FINE_THRESHOLDS[-1] == 0.20
    assert len(FINE_THRESHOLDS) == 21


def test_threshold_zero_equals_review_all() -> None:
    row = policy_counts(
        [NOT_APPLIES, APPLIES, APPLIES],
        [0.9, 0.4, 0.1],
        0.0,
    )
    assert row["manual_reviews"] == 3
    assert row["released_rows"] == 0
    assert row["total_cost_units"] == pytest.approx(row["review_all_cost_units"])
    assert row["delta_vs_review_all"] == pytest.approx(0.0)


def test_cost_counts_are_auditable() -> None:
    row = policy_counts(
        [NOT_APPLIES, NOT_APPLIES, APPLIES, APPLIES],
        [0.9, 0.2, 0.8, 0.1],
        0.5,
    )
    assert row["manual_reviews"] == 2
    assert row["false_applies"] == 1
    assert row["applies_reviewed"] == 1
    assert row["total_cost_units"] == pytest.approx(14.0)


def test_gate_rejects_uncertain_release_and_non_strict_cost() -> None:
    row = policy_counts([NOT_APPLIES, APPLIES], [0.9, 0.1], 0.5)
    passed, reasons = automatic_release_gate(
        row,
        {"upper_95": 0.0},
    )
    assert passed is False
    assert "release_risk_not_certified" in reasons
    assert "cost_saving_not_strictly_below_zero" in reasons
