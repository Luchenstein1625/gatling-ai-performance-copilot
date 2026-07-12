from pathlib import Path
from typing import Any

from performance_decision_engine.application.ports.configuration_reader import ConfigurationReader
from performance_decision_engine.domain.entities.configuration import (
    EndpointConfiguration,
    PerformanceConfiguration,
    ResolvedTriplet,
)
from performance_decision_engine.infrastructure.parsers.parameter_values import ParameterValues
from performance_decision_engine.infrastructure.parsers.yaml_loader import load_yaml


class YamlConfigurationReader(ConfigurationReader):
    def read(
        self,
        performance_path: Path,
        parameters_path: Path,
    ) -> PerformanceConfiguration:
        document = load_yaml(performance_path)
        parameters = ParameterValues.from_file(parameters_path)

        warnings: list[str] = []
        endpoints: list[EndpointConfiguration] = []

        raw_features = document.get("features", [])
        if not isinstance(raw_features, list):
            warnings.append("The 'features' field is not a list")
            raw_features = []

        for index, raw in enumerate(raw_features):
            if not isinstance(raw, dict):
                warnings.append(f"Feature at index {index} is not an object")
                continue

            endpoints.append(self._map_endpoint(raw, index, parameters))

        load_type = document.get("loadType")
        return PerformanceConfiguration(
            load_type=str(load_type) if load_type is not None else None,
            endpoints=endpoints,
            warnings=warnings,
        )

    def _map_endpoint(
        self,
        raw: dict[str, Any],
        index: int,
        parameters: ParameterValues,
    ) -> EndpointConfiguration:
        concurrency = str(raw.get("concurrency", "unknown"))
        iterations = str(raw.get("iterations", "unknown"))
        response_time = str(raw.get("response_time", "unknown"))

        return EndpointConfiguration(
            name=str(raw.get("name", f"endpoint-{index}")),
            feature_reference=str(raw.get("feature", "")),
            enabled=bool(raw.get("performance", False)),
            reason=self._optional_text(raw.get("reason")),
            reason_detail=self._optional_text(raw.get("reason_detail")),
            triplet=ResolvedTriplet(
                concurrency_level=concurrency,
                concurrency_value=self._optional_int(
                    parameters.resolve("concurrency", concurrency)
                ),
                iterations_level=iterations,
                iterations_value=self._optional_int(
                    parameters.resolve("iterations", iterations)
                ),
                response_time_level=response_time,
                response_time_ms=self._optional_int(
                    parameters.resolve("response_time", response_time)
                ),
            ),
        )

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        return str(value) if value is not None else None

    @staticmethod
    def _optional_int(value: int | float | None) -> int | None:
        return int(value) if value is not None else None
