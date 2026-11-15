from performance_decision_engine.infrastructure.calibration_audit_v3_1 import order_effects


def test_strict_monotonic_transform_preserves_order() -> None:
    result = order_effects([0.1, 0.2, 0.9], [0.2, 0.4, 0.8])
    assert result["order_inversions"] == 0
    assert result["new_tied_pairs"] == 0


def test_isotonic_style_blocks_create_ties_without_inversions() -> None:
    result = order_effects([0.1, 0.2, 0.9], [0.3, 0.3, 0.8])
    assert result["order_inversions"] == 0
    assert result["new_tied_pairs"] == 1


def test_reversed_scores_are_detected() -> None:
    result = order_effects([0.1, 0.9], [0.8, 0.2])
    assert result["order_inversions"] == 1

