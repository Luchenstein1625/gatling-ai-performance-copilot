from __future__ import annotations

from math import isfinite
from typing import Any

TRUE_VALUES = {"true", "1", "yes", "y", "si", "sí", "enabled", "on"}
FALSE_VALUES = {"false", "0", "no", "n", "disabled", "off", ""}


def normalize_text(
    value: Any,
    *,
    default: str | None = None,
    lowercase: bool = False,
) -> str | None:
    """Normalize arbitrary input into a trimmed string."""
    if value is None:
        return default
    normalized = str(value).strip()
    if not normalized:
        return default
    return normalized.lower() if lowercase else normalized


def normalize_boolean(value: Any, *, default: bool = False) -> bool:
    """Convert common YAML, JSON and textual representations to bool."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)

    normalized = str(value).strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(f"Cannot normalize boolean value: {value!r}")


def normalize_non_negative_int(
    value: Any,
    *,
    field_name: str,
    required: bool = False,
) -> int | None:
    """Normalize a numeric value into a non-negative integer."""
    if value is None or value == "":
        if required:
            raise ValueError(f"Missing required field: {field_name}")
        return None
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer")
    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc
    if not isfinite(numeric_value):
        raise ValueError(f"{field_name} must be finite")
    if numeric_value < 0:
        raise ValueError(f"{field_name} cannot be negative")
    if not numeric_value.is_integer():
        raise ValueError(f"{field_name} must be an integer")
    return int(numeric_value)


def normalize_non_negative_float(
    value: Any,
    *,
    field_name: str,
    required: bool = False,
) -> float | None:
    """Normalize a numeric value into a non-negative float."""
    if value is None or value == "":
        if required:
            raise ValueError(f"Missing required field: {field_name}")
        return None
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc
    if not isfinite(result):
        raise ValueError(f"{field_name} must be finite")
    if result < 0:
        raise ValueError(f"{field_name} cannot be negative")
    return result


def calculate_error_rate(total_requests: int, failed_requests: int) -> float:
    """Calculate the error percentage safely."""
    if total_requests < 0 or failed_requests < 0:
        raise ValueError("Request counts cannot be negative")
    if failed_requests > total_requests:
        raise ValueError("Failed requests cannot exceed total requests")
    if total_requests == 0:
        return 0.0
    return round((failed_requests / total_requests) * 100.0, 6)


def merge_warnings(*warning_groups: list[str]) -> list[str]:
    """Merge warnings while preserving order and removing duplicates."""
    result: list[str] = []
    seen: set[str] = set()
    for warning_group in warning_groups:
        for warning in warning_group:
            normalized = warning.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(normalized)
    return result
