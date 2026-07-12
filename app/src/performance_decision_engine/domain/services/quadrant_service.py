from performance_decision_engine.domain.entities.quadrant import Quadrant

_MATRIX: dict[tuple[str, str], int] = {
    ("low", "low"): 1,
    ("medium", "low"): 2,
    ("high", "low"): 3,
    ("low", "medium"): 4,
    ("medium", "medium"): 5,
    ("high", "medium"): 6,
    ("low", "high"): 7,
    ("medium", "high"): 8,
    ("high", "high"): 9,
}


def resolve_quadrant(criticality: str, complexity: str) -> Quadrant:
    key = (criticality.lower().strip(), complexity.lower().strip())
    if key not in _MATRIX:
        raise ValueError(f"Unsupported criticality/complexity combination: {key}")

    return Quadrant(
        number=_MATRIX[key],
        criticality=key[0],
        complexity=key[1],
    )
