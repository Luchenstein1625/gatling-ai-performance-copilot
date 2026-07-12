import json
from pathlib import Path

import pytest

from performance_decision_engine.infrastructure.parsers.gatling_metrics_reader import (
    GatlingMetricsReader,
)


def write_json(path: Path, content: object) -> Path:
    path.write_text(json.dumps(content), encoding="utf-8")
    return path


def valid_global_stats() -> dict[str, object]:
    return {
        "stats": {
            "numberOfRequests": {"total": 100, "ok": 95, "ko": 5},
            "minResponseTime": {"total": 10},
            "meanResponseTime": {"total": 120},
            "maxResponseTime": {"total": 900},
            "percentiles1": {"total": 100},
            "percentiles2": {"total": 150},
            "percentiles3": {"total": 300},
            "percentiles4": {"total": 600},
            "meanNumberOfRequestsPerSecond": {"total": 25.5},
        }
    }


def test_reads_global_gatling_metrics(tmp_path: Path) -> None:
    metrics_path = write_json(tmp_path / "global_stats.json", valid_global_stats())

    metrics = GatlingMetricsReader().read(metrics_path)

    assert metrics.total_requests == 100
    assert metrics.successful_requests == 95
    assert metrics.failed_requests == 5
    assert metrics.error_rate_percent == pytest.approx(5.0)
    assert metrics.min_response_time_ms == 10
    assert metrics.mean_response_time_ms == 120
    assert metrics.max_response_time_ms == 900
    assert metrics.p50_response_time_ms == 100
    assert metrics.p75_response_time_ms == 150
    assert metrics.p95_response_time_ms == 300
    assert metrics.p99_response_time_ms == 600
    assert metrics.requests_per_second == pytest.approx(25.5)
    assert metrics.assertions is None


def test_reads_metrics_without_optional_values(tmp_path: Path) -> None:
    metrics_path = write_json(
        tmp_path / "global_stats.json",
        {
            "numberOfRequests": {
                "total": 0,
                "ok": 0,
                "ko": 0,
            }
        },
    )

    metrics = GatlingMetricsReader().read(metrics_path)

    assert metrics.error_rate_percent == 0.0
    assert metrics.mean_response_time_ms is None
    assert metrics.p95_response_time_ms is None
    assert metrics.requests_per_second is None


def test_rejects_missing_required_request_count(tmp_path: Path) -> None:
    content = valid_global_stats()
    stats = content["stats"]
    assert isinstance(stats, dict)
    requests = stats["numberOfRequests"]
    assert isinstance(requests, dict)
    del requests["ko"]

    metrics_path = write_json(tmp_path / "global_stats.json", content)

    with pytest.raises(ValueError, match="numberOfRequests.ko"):
        GatlingMetricsReader().read(metrics_path)


def test_rejects_inconsistent_request_counts(tmp_path: Path) -> None:
    content = valid_global_stats()
    stats = content["stats"]
    assert isinstance(stats, dict)
    requests = stats["numberOfRequests"]
    assert isinstance(requests, dict)
    requests["total"] = 101

    metrics_path = write_json(tmp_path / "global_stats.json", content)

    with pytest.raises(ValueError, match="total requests"):
        GatlingMetricsReader().read(metrics_path)


def test_rejects_invalid_json(tmp_path: Path) -> None:
    metrics_path = tmp_path / "global_stats.json"
    metrics_path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        GatlingMetricsReader().read(metrics_path)


def test_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="File not found"):
        GatlingMetricsReader().read(tmp_path / "missing.json")
