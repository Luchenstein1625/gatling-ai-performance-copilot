from pathlib import Path

from performance_decision_engine.parsers.parameter_values import ParameterResolver


def test_resolve_parameter() -> None:
    path = Path("examples/input/parametricConfigurationValues.yaml")
    resolver = ParameterResolver.from_file(path)
    assert resolver.resolve("concurrency", "high") == 60
    assert resolver.resolve("response_time", "very_high") == 15000
