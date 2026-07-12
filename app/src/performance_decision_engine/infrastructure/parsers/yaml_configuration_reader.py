from pathlib import Path
from typing import Any

from performance_decision_engine.application.ports.configuration_reader import ConfigurationReader
from performance_decision_engine.domain.entities.configuration import (
    EndpointConfiguration,
    PerformanceConfiguration,
    ResolvedTriplet,
)
from performance_decision_engine.domain.services.normalization_service import (
    normalize_boolean,
    normalize_text,
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
            try:
                endpoints.append(self._map_endpoint(raw, index, parameters))
            except ValueError as exc:
                raise ValueError(f"Invalid feature at index {index}: {exc}") from exc

        load_type = normalize_text(document.get("loadType"), lowercase=True)
        return PerformanceConfiguration(
            load_type=load_type,
            endpoints=endpoints,
            warnings=warnings,
        )

    def _map_endpoint(
        self,
        raw: dict[str, Any],
        index: int,
        parameters: ParameterValues,
    ) -> EndpointConfiguration:
        concurrency = normalize_text(raw.get("concurrency"), default="unknown", lowercase=True)
        iterations = normalize_text(raw.get("iterations"), default="unknown", lowercase=True)
        response_time = normalize_text(raw.get("response_time"), default="unknown", lowercase=True)
        assert concurrency is not None
        assert iterations is not None
        assert response_time is not None

        return EndpointConfiguration(
            name=normalize_text(raw.get("name"), default=f"endpoint-{index}")
            or f"endpoint-{index}",
            feature_reference=normalize_text(raw.get("feature"), default="") or "",
            enabled=normalize_boolean(raw.get("performance"), default=False),
            reason=normalize_text(raw.get("reason")),
            reason_detail=normalize_text(raw.get("reason_detail")),
            triplet=ResolvedTriplet(
                concurrency_level=concurrency,
                concurrency_value=self._optional_int(
                    parameters.resolve("concurrency", concurrency)
                ),
                iterations_level=iterations,
                iterations_value=self._optional_int(parameters.resolve("iterations", iterations)),
                response_time_level=response_time,
                response_time_ms=self._optional_int(
                    parameters.resolve("response_time", response_time)
                ),
            ),
        )

    @staticmethod
    def _optional_int(value: int | float | None) -> int | None:
        return int(value) if value is not None else None
