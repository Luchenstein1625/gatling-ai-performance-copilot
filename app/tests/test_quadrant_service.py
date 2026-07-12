import pytest

from performance_decision_engine.domain.services.quadrant_service import resolve_quadrant


@pytest.mark.parametrize(
    ("criticality", "complexity", "expected"),
    [
        ("low", "low", 1),
        ("medium", "medium", 5),
        ("high", "medium", 6),
        ("high", "high", 9),
    ],
)
def test_resolve_quadrant(
    criticality: str,
    complexity: str,
    expected: int,
) -> None:
    assert resolve_quadrant(criticality, complexity).number == expected
