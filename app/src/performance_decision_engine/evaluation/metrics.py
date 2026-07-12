def exact_match(expected: list[int], predicted: list[int]) -> float:
    if len(expected) != len(predicted):
        raise ValueError("Expected and predicted must have the same length")
    if not expected:
        return 0.0
    matches = sum(1 for left, right in zip(expected, predicted, strict=True) if left == right)
    return matches / len(expected)
