from pydantic import BaseModel


class QuadrantProfile(BaseModel):
    quadrant: int
    criticality: str
    complexity: str


_QUADRANTS: dict[tuple[str, str], int] = {
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


def resolve_quadrant(criticality: str, complexity: str) -> QuadrantProfile:
    key = (criticality.lower(), complexity.lower())
    if key not in _QUADRANTS:
        raise ValueError(f"Unsupported criticality/complexity combination: {key}")
    return QuadrantProfile(
        quadrant=_QUADRANTS[key],
        criticality=key[0],
        complexity=key[1],
    )
