from pathlib import Path

from performance_decision_engine.domain.models import ExecutionSummary
from performance_decision_engine.parsers.gatling_global import parse_gatling_global
from performance_decision_engine.parsers.parameter_values import ParameterResolver
from performance_decision_engine.parsers.performance_yaml import parse_performance_yaml


def build_execution_summary(
    performance_path: Path,
    parameters_path: Path,
    gatling_path: Path,
) -> ExecutionSummary:
    resolver = ParameterResolver.from_file(parameters_path)
    load_type, features, warnings = parse_performance_yaml(performance_path, resolver)
    gatling = parse_gatling_global(gatling_path)

    return ExecutionSummary(
        load_type=load_type,
        features=features,
        gatling_global=gatling,
        warnings=warnings,
    )
