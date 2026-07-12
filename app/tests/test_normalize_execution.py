from pathlib import Path

from performance_decision_engine.application.use_cases.normalize_execution import (
    NormalizeExecution,
)
from performance_decision_engine.infrastructure.parsers.gatling_metrics_reader import (
    GatlingMetricsReader,
)
from performance_decision_engine.infrastructure.parsers.yaml_configuration_reader import (
    YamlConfigurationReader,
)


def test_normalize_execution_example() -> None:
    use_case = NormalizeExecution(
        configuration_reader=YamlConfigurationReader(),
        metrics_reader=GatlingMetricsReader(),
    )

    result = use_case.execute(
        performance_path=Path("examples/input/performance.yaml"),
        parameters_path=Path("examples/input/parametricConfigurationValues.yaml"),
        results_path=Path("examples/input/global_stats.json"),
    )

    assert result.configuration.load_type == "sequence"
    assert len(result.configuration.endpoints) == 2
    assert result.configuration.endpoints[0].triplet.concurrency_value == 20
    assert result.configuration.endpoints[1].triplet.response_time_ms == 15000
    assert result.global_metrics.total_requests == 2801
    assert result.global_metrics.failed_requests == 0
