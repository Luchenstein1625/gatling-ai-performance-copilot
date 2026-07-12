from pathlib import Path

from performance_decision_engine.application.ports.configuration_reader import ConfigurationReader
from performance_decision_engine.application.ports.metrics_reader import MetricsReader
from performance_decision_engine.domain.entities.execution import NormalizedExecution


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
    ) -> NormalizedExecution:
        configuration = self.configuration_reader.read(performance_path, parameters_path)
        metrics = self.metrics_reader.read(results_path)

        return NormalizedExecution(
            configuration=configuration,
            global_metrics=metrics,
            warnings=list(configuration.warnings),
        )
