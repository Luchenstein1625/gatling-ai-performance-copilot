from performance_decision_engine.evaluation.metrics import exact_match


def test_exact_match() -> None:
    assert exact_match([1, 2, 3], [1, 2, 9]) == 2 / 3
