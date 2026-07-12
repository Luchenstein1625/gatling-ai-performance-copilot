import json
from pathlib import Path
from typing import Any

from performance_decision_engine.application.ports.metrics_reader import MetricsReader
from performance_decision_engine.domain.entities.execution import ExecutionMetrics


class GatlingMetricsReader(MetricsReader):
    def read(self, path: Path) -> ExecutionMetrics:
        if not path.exists():
            raise ValueError(f"File not found: {path}")

        try:
            raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON file: {path}") from exc

        stats = raw.get("stats", raw)
        if not isinstance(stats, dict):
            raise ValueError("Invalid metrics document")

        total = self._required_int(stats, "numberOfRequests", "total")
        successful = self._required_int(stats, "numberOfRequests", "ok")
        failed = self._required_int(stats, "numberOfRequests", "ko")

        return ExecutionMetrics(
            total_requests=total,
            successful_requests=successful,
            failed_requests=failed,
            error_rate_percent=(failed / total * 100.0) if total else 0.0,
            min_response_time_ms=self._optional_int(stats, "minResponseTime", "total"),
            mean_response_time_ms=self._optional_int(stats, "meanResponseTime", "total"),
            max_response_time_ms=self._optional_int(stats, "maxResponseTime", "total"),
            p95_response_time_ms=self._optional_int(stats, "percentiles3", "total"),
            p99_response_time_ms=self._optional_int(stats, "percentiles4", "total"),
            requests_per_second=self._optional_float(
                stats,
                "meanNumberOfRequestsPerSecond",
                "total",
            ),
        )

    @staticmethod
    def _nested(data: dict[str, Any], first: str, second: str) -> Any:
        value = data.get(first)
        if isinstance(value, dict):
            return value.get(second)
        return None

    @classmethod
    def _required_int(cls, data: dict[str, Any], first: str, second: str) -> int:
        value = cls._nested(data, first, second)
        return int(value or 0)

    @classmethod
    def _optional_int(
        cls,
        data: dict[str, Any],
        first: str,
        second: str,
    ) -> int | None:
        value = cls._nested(data, first, second)
        return int(value) if value is not None else None

    @classmethod
    def _optional_float(
        cls,
        data: dict[str, Any],
        first: str,
        second: str,
    ) -> float | None:
        value = cls._nested(data, first, second)
        return float(value) if value is not None else None
