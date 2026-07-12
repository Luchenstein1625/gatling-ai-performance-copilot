from pathlib import Path

from performance_decision_engine.application.ports.configuration_reader import ConfigurationReader
from performance_decision_engine.application.ports.metrics_reader import MetricsReader
from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.services.normalization_service import merge_warnings


class NormalizeExecution:
    def __init__(
        self,
        configuration_reader: ConfigurationReader,
        metrics_reader: MetricsReader,
    ) -> None:
        self.configuration_reader = configuration_reader
        self.metrics_reader = metrics_reader

    def execute(
        self,
        performance_path: Path,
        parameters_path: Path,
        results_path: Path,
        assertions_path: Path | None = None,
    ) -> NormalizedExecution:
        configuration = self.configuration_reader.read(performance_path, parameters_path)
        metrics = self.metrics_reader.read(results_path, assertions_path=assertions_path)

        warnings = list(configuration.warnings)
        if not configuration.endpoints:
            warnings.append("No endpoints were found in performance.yaml")
        if not any(endpoint.enabled for endpoint in configuration.endpoints):
            warnings.append("No enabled endpoints were found")

        for endpoint in configuration.endpoints:
            triplet = endpoint.triplet
            if (
                triplet.concurrency_value is None
                or triplet.iterations_value is None
                or triplet.response_time_ms is None
            ):
                warnings.append(f"Endpoint '{endpoint.name}' contains unresolved triplet values")

        if metrics.total_requests == 0:
            warnings.append("The Gatling execution contains zero requests")
        if metrics.failed_requests > 0:
            warnings.append(f"The execution contains {metrics.failed_requests} failed requests")
        if metrics.assertions is not None and not metrics.assertions.all_passed:
            warnings.append("One or more Gatling assertions failed")

        return NormalizedExecution(
            configuration=configuration,
            global_metrics=metrics,
            warnings=merge_warnings(warnings),
        )
