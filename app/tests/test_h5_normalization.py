import json
from pathlib import Path

from performance_decision_engine.infrastructure.parsers.gatling_metrics_reader import (
    GatlingMetricsReader,
)
from performance_decision_engine.infrastructure.parsers.yaml_configuration_reader import (
    YamlConfigurationReader,
)


def test_yaml_reader_interprets_false_string_as_disabled(tmp_path: Path) -> None:
    performance_file = tmp_path / "performance.yaml"
    parameters_file = tmp_path / "parameters.yaml"
    performance_file.write_text(
        """
loadType: stress
features:
  - name: consulta-saldo
    feature: saldo.feature
    performance: "false"
    concurrency: medium
    iterations: medium
    response_time: medium
""",
        encoding="utf-8",
    )
    parameters_file.write_text(
        """
concurrency:
  medium: 20
iterations:
  medium: 100
response_time:
  medium: 2000
""",
        encoding="utf-8",
    )
    configuration = YamlConfigurationReader().read(performance_file, parameters_file)
    assert len(configuration.endpoints) == 1
    assert configuration.endpoints[0].enabled is False


def test_gatling_reader_normalizes_p90_when_explicit(tmp_path: Path) -> None:
    metrics_file = tmp_path / "global_stats.json"
    metrics_file.write_text(
        json.dumps(
            {
                "stats": {
                    "numberOfRequests": {"total": 100, "ok": 98, "ko": 2},
                    "p90": {"total": 850},
                    "percentiles3": {"total": 1200},
                    "percentiles4": {"total": 1500},
                    "meanNumberOfRequestsPerSecond": {"total": 25.5},
                }
            }
        ),
        encoding="utf-8",
    )
    metrics = GatlingMetricsReader().read(metrics_file)
    assert metrics.p90_response_time_ms == 850
    assert metrics.p95_response_time_ms == 1200
    assert metrics.error_rate_percent == 2.0
