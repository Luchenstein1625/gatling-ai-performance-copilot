from pathlib import Path

import pytest

from performance_decision_engine.infrastructure.parsers.parameter_values import (
    ParameterValues,
    UnknownParameterLevelError,
)


PARAMETERS_FILE = Path("examples/input/parametricConfigurationValues.yaml")


def test_loads_parameter_values_file() -> None:
    values = ParameterValues.from_file(PARAMETERS_FILE)

    assert values.resolve_concurrency("high") == 60
    assert values.resolve_iterations("medium") == 7
    assert values.resolve_response_time("very_high") == 15000
    assert values.success_rate == 100


def test_normalizes_level_case_and_spaces() -> None:
    values = ParameterValues.from_file(PARAMETERS_FILE)

    assert values.resolve_concurrency(" HIGH ") == 60


def test_unknown_level_returns_none_by_default() -> None:
    values = ParameterValues.from_file(PARAMETERS_FILE)

    assert values.resolve_concurrency("critical") is None


def test_unknown_level_raises_in_strict_mode() -> None:
    values = ParameterValues.from_file(PARAMETERS_FILE)

    with pytest.raises(UnknownParameterLevelError):
        values.resolve_concurrency("critical", strict=True)
