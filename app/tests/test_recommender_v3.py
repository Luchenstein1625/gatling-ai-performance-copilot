from performance_decision_engine.infrastructure.recommender_v3 import (
    CellStats,
    apply_stability_guardrail,
    recommendation,
    stricter_neighbors,
)


def stats(rate: float, lower: float, upper: float, rows: int = 50, builds: int = 10) -> CellStats:
    applies = round(rate * rows)
    return CellStats(rows, builds, applies, rows - applies, rate, lower, upper)


def test_stricter_neighbors_change_one_level_only() -> None:
    neighbors = dict(stricter_neighbors(("low", "low", "high")))
    assert neighbors["Concurrency"] == ("medium", "low", "high")
    assert neighbors["Iterations"] == ("low", "medium", "high")
    assert neighbors["ResponseTime"] == ("low", "low", "medium")


def test_insufficient_support_abstains() -> None:
    cell = ("low", "low", "high")
    result = recommendation(cell, {cell: stats(0.8, 0.7, 0.9, rows=10)}, 0.7, 0.5, 20)
    assert result["action"] == "abstain"


def test_low_upper_bound_routes_to_review() -> None:
    cell = ("low", "low", "high")
    result = recommendation(cell, {cell: stats(0.2, 0.1, 0.3)}, 0.7, 0.4, 20)
    assert result["action"] == "review"


def test_supported_stricter_neighbor_upgrades() -> None:
    cell = ("low", "low", "high")
    target = ("medium", "low", "high")
    result = recommendation(
        cell,
        {cell: stats(0.8, 0.7, 0.9), target: stats(0.85, 0.75, 0.93)},
        0.7,
        0.5,
        20,
    )
    assert result["action"] == "upgrade"
    assert result["changed_parameter"] == "Concurrency"
    assert result["to_real_value"] == 40


def test_uncertain_current_cell_abstains() -> None:
    cell = ("low", "low", "high")
    result = recommendation(cell, {cell: stats(0.5, 0.3, 0.7)}, 0.8, 0.5, 20)
    assert result["action"] == "abstain"


def test_unstable_upgrade_is_published_as_abstain() -> None:
    guarded = apply_stability_guardrail(
        {"cell": "medium|medium|high", "action": "upgrade"}, 0.624
    )
    assert guarded["action_estimated"] == "upgrade"
    assert guarded["action_published"] == "abstain"
    assert guarded["experimental_candidate"] == "upgrade"


def test_stable_action_is_publishable() -> None:
    guarded = apply_stability_guardrail(
        {"cell": "low|low|medium", "action": "maintain"}, 0.90
    )
    assert guarded["action_published"] == "maintain"
    assert guarded["experimental_candidate"] is None
