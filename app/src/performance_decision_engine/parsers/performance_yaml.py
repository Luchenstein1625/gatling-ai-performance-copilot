from pathlib import Path
from typing import Any

from performance_decision_engine.domain.models import (
    FeatureConfiguration,
    ResolvedTriplet,
)
from performance_decision_engine.parsers.parameter_values import ParameterResolver
from performance_decision_engine.parsers.yaml_loader import load_yaml


def parse_performance_yaml(
    path: Path,
    resolver: ParameterResolver,
) -> tuple[str | None, list[FeatureConfiguration], list[str]]:
    raw = load_yaml(path)
    warnings: list[str] = []
    features: list[FeatureConfiguration] = []

    for index, item in enumerate(raw.get("features", [])):
        if not isinstance(item, dict):
            warnings.append(f"Feature at index {index} is not an object")
            continue

        concurrency = str(item.get("concurrency", "unknown"))
        iterations = str(item.get("iterations", "unknown"))
        response_time = str(item.get("response_time", "unknown"))

        triplet = ResolvedTriplet(
            concurrency_level=concurrency,
            concurrency_value=_as_int(resolver.resolve("concurrency", concurrency)),
            iterations_level=iterations,
            iterations_value=_as_int(resolver.resolve("iterations", iterations)),
            response_time_level=response_time,
            response_time_ms=_as_int(resolver.resolve("response_time", response_time)),
        )

        features.append(
            FeatureConfiguration(
                name=str(item.get("name", f"feature-{index}")),
                feature=str(item.get("feature", "")),
                performance=bool(item.get("performance", False)),
                reason=item.get("reason"),
                reason_detail=item.get("reason_detail"),
                triplet=triplet,
            )
        )

    return raw.get("loadType"), features, warnings


def _as_int(value: int | float | None) -> int | None:
    return int(value) if value is not None else None
