from performance_decision_engine.infrastructure.recommender_audit_v3_1 import EXPECTED_ORDER
from performance_decision_engine.infrastructure.recommender_v3 import LEVELS, stricter_neighbors


def test_response_time_order_is_stricter_toward_lower_milliseconds() -> None:
    assert tuple(LEVELS["ResponseTime"]) == ("very_high", "high", "medium", "low")
    assert tuple(LEVELS["ResponseTime"]) == EXPECTED_ORDER["ResponseTime"]


def test_high_response_time_neighbor_is_medium() -> None:
    neighbors = dict(stricter_neighbors(("medium", "medium", "high")))
    assert neighbors["ResponseTime"] == ("medium", "medium", "medium")


def test_load_dimensions_increase_toward_stricter_values() -> None:
    assert tuple(LEVELS["Concurrency"]) == EXPECTED_ORDER["Concurrency"]
    assert tuple(LEVELS["Iterations"]) == EXPECTED_ORDER["Iterations"]

