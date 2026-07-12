import pytest

from performance_decision_engine.domain.services.normalization_service import (
    calculate_error_rate,
    merge_warnings,
    normalize_boolean,
    normalize_non_negative_float,
    normalize_non_negative_int,
    normalize_text,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (True, True),
        (False, False),
        ("true", True),
        ("TRUE", True),
        ("yes", True),
        ("sí", True),
        ("1", True),
        (1, True),
        ("false", False),
        ("FALSE", False),
        ("no", False),
        ("0", False),
        (0, False),
        (None, False),
    ],
)
def test_normalize_boolean(raw: object, expected: bool) -> None:
    assert normalize_boolean(raw) is expected


def test_normalize_boolean_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="Cannot normalize boolean"):
        normalize_boolean("perhaps")


def test_normalize_text_removes_surrounding_spaces() -> None:
    assert normalize_text("  endpoint-one  ") == "endpoint-one"


def test_normalize_non_negative_int() -> None:
    assert normalize_non_negative_int("25", field_name="requests") == 25


def test_normalize_non_negative_int_rejects_decimal() -> None:
    with pytest.raises(ValueError, match="must be an integer"):
        normalize_non_negative_int("25.5", field_name="requests")


def test_normalize_non_negative_float() -> None:
    assert normalize_non_negative_float("25.5", field_name="tps") == 25.5


def test_calculate_error_rate() -> None:
    assert calculate_error_rate(200, 10) == 5.0


def test_calculate_error_rate_with_zero_requests() -> None:
    assert calculate_error_rate(0, 0) == 0.0


def test_merge_warnings_removes_duplicates() -> None:
    assert merge_warnings(
        ["First warning", "Second warning"],
        ["Second warning", "Third warning"],
    ) == ["First warning", "Second warning", "Third warning"]
