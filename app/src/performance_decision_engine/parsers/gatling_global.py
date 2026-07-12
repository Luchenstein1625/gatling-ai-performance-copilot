import json
from pathlib import Path
from typing import Any

from performance_decision_engine.core.exceptions import InputFileError
from performance_decision_engine.domain.models import GatlingGlobalMetrics


def parse_gatling_global(path: Path) -> GatlingGlobalMetrics:
    if not path.exists():
        raise InputFileError(f"File not found: {path}")

    try:
        raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputFileError(f"Invalid JSON file: {path}") from exc

    stats = raw.get("stats", raw)

    total = _number(stats, "numberOfRequests", "total")
    ok = _number(stats, "numberOfRequests", "ok")
    ko = _number(stats, "numberOfRequests", "ko")
    error_rate = (ko / total * 100.0) if total else 0.0

    return GatlingGlobalMetrics(
        total_requests=total,
        successful_requests=ok,
        failed_requests=ko,
        error_rate=error_rate,
        min_response_time_ms=_optional_number(stats, "minResponseTime", "total"),
        mean_response_time_ms=_optional_number(stats, "meanResponseTime", "total"),
        max_response_time_ms=_optional_number(stats, "maxResponseTime", "total"),
        p95_response_time_ms=_optional_number(stats, "percentiles3", "total"),
        p99_response_time_ms=_optional_number(stats, "percentiles4", "total"),
        requests_per_second=_optional_float(stats, "meanNumberOfRequestsPerSecond", "total"),
    )


def _nested(data: dict[str, Any], first: str, second: str) -> Any:
    value = data.get(first, {})
    return value.get(second) if isinstance(value, dict) else None


def _number(data: dict[str, Any], first: str, second: str) -> int:
    value = _nested(data, first, second)
    return int(value or 0)


def _optional_number(data: dict[str, Any], first: str, second: str) -> int | None:
    value = _nested(data, first, second)
    return int(value) if value is not None else None


def _optional_float(data: dict[str, Any], first: str, second: str) -> float | None:
    value = _nested(data, first, second)
    return float(value) if value is not None else None
