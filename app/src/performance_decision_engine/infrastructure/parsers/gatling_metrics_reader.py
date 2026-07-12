import json
from pathlib import Path
from typing import Any

from performance_decision_engine.application.ports.metrics_reader import MetricsReader
from performance_decision_engine.domain.entities.execution import ExecutionMetrics
from performance_decision_engine.domain.services.normalization_service import calculate_error_rate
from performance_decision_engine.infrastructure.parsers.gatling_assertions_reader import (
    GatlingAssertionsReader,
)


class GatlingMetricsReader(MetricsReader):
    """Read and normalize a Gatling global_stats.json document."""

    def read(
        self,
        path: Path,
        assertions_path: Path | None = None,
    ) -> ExecutionMetrics:
        raw = self._load_json(path)
        stats = raw.get("stats", raw)
        if not isinstance(stats, dict):
            raise ValueError("Invalid metrics document: 'stats' must be an object")

        total = self._required_int(stats, "numberOfRequests", "total")
        successful = self._required_int(stats, "numberOfRequests", "ok")
        failed = self._required_int(stats, "numberOfRequests", "ko")
        if total != successful + failed:
            raise ValueError(
                "Invalid metrics document: total requests must equal "
                "successful requests plus failed requests"
            )

        assertions = (
            GatlingAssertionsReader().read(assertions_path) if assertions_path is not None else None
        )

        return ExecutionMetrics(
            total_requests=total,
            successful_requests=successful,
            failed_requests=failed,
            error_rate_percent=calculate_error_rate(total, failed),
            min_response_time_ms=self._optional_int(stats, "minResponseTime", "total"),
            mean_response_time_ms=self._optional_int(stats, "meanResponseTime", "total"),
            max_response_time_ms=self._optional_int(stats, "maxResponseTime", "total"),
            p50_response_time_ms=self._first_optional_int(
                stats, (("p50", "total"), ("percentiles1", "total"))
            ),
            p75_response_time_ms=self._first_optional_int(
                stats, (("p75", "total"), ("percentiles2", "total"))
            ),
            p90_response_time_ms=self._first_optional_int(
                stats, (("p90", "total"), ("percentile90", "total"))
            ),
            p95_response_time_ms=self._first_optional_int(
                stats, (("p95", "total"), ("percentiles3", "total"))
            ),
            p99_response_time_ms=self._first_optional_int(
                stats, (("p99", "total"), ("percentiles4", "total"))
            ),
            requests_per_second=self._optional_float(
                stats, "meanNumberOfRequestsPerSecond", "total"
            ),
            assertions=assertions,
        )

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise ValueError(f"File not found: {path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        try:
            raw: Any = json.loads(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as exc:
            raise ValueError(f"File is not valid UTF-8: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON file: {path}") from exc
        if not isinstance(raw, dict):
            raise ValueError("Invalid metrics document: expected a JSON object")
        return raw

    @staticmethod
    def _nested(data: dict[str, Any], first: str, second: str) -> Any:
        value = data.get(first)
        if not isinstance(value, dict):
            return None
        return value.get(second)

    @classmethod
    def _required_int(cls, data: dict[str, Any], first: str, second: str) -> int:
        result = cls._optional_int(data, first, second)
        if result is None:
            raise ValueError(f"Invalid metrics document: missing '{first}.{second}'")
        return result

    @classmethod
    def _optional_int(cls, data: dict[str, Any], first: str, second: str) -> int | None:
        value = cls._nested(data, first, second)
        if value is None:
            return None
        if isinstance(value, bool):
            raise ValueError(f"Invalid metrics document: '{first}.{second}' must be an integer")
        try:
            result = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid metrics document: '{first}.{second}' must be an integer"
            ) from exc
        if result < 0:
            raise ValueError(f"Invalid metrics document: '{first}.{second}' cannot be negative")
        return result

    @classmethod
    def _first_optional_int(
        cls,
        data: dict[str, Any],
        candidates: tuple[tuple[str, str], ...],
    ) -> int | None:
        for first, second in candidates:
            if cls._nested(data, first, second) is not None:
                return cls._optional_int(data, first, second)
        return None

    @classmethod
    def _optional_float(cls, data: dict[str, Any], first: str, second: str) -> float | None:
        value = cls._nested(data, first, second)
        if value is None:
            return None
        if isinstance(value, bool):
            raise ValueError(f"Invalid metrics document: '{first}.{second}' must be numeric")
        try:
            result = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid metrics document: '{first}.{second}' must be numeric"
            ) from exc
        if result < 0:
            raise ValueError(f"Invalid metrics document: '{first}.{second}' cannot be negative")
        return result
