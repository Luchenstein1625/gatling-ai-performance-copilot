import json
from pathlib import Path

import pytest

from performance_decision_engine.infrastructure.parsers.gatling_assertions_reader import (
    GatlingAssertionsReader,
)
from performance_decision_engine.infrastructure.parsers.gatling_metrics_reader import (
    GatlingMetricsReader,
)


def write_json(path: Path, content: object) -> Path:
    path.write_text(json.dumps(content), encoding="utf-8")
    return path


def test_reads_assertions_collection(tmp_path: Path) -> None:
    assertions_path = write_json(
        tmp_path / "assertions.json",
        {
            "assertions": [
                {
                    "path": "Global",
                    "target": "responseTime.percentile3",
                    "condition": "lt",
                    "expected": 2000,
                    "actual": 850,
                    "successful": True,
                    "message": "p95 is below the SLA",
                },
                {
                    "path": "Global",
                    "target": "failedRequests.percent",
                    "condition": "lte",
                    "expected": 1,
                    "actual": 2.5,
                    "successful": False,
                    "message": "error rate exceeded",
                },
            ]
        },
    )

    summary = GatlingAssertionsReader().read(assertions_path)

    assert summary.total == 2
    assert summary.successful == 1
    assert summary.failed == 1
    assert summary.all_passed is False
    assert summary.results[0].target == "responseTime.percentile3"
    assert summary.results[1].successful is False


def test_accepts_status_based_assertions(tmp_path: Path) -> None:
    assertions_path = write_json(
        tmp_path / "assertions.json",
        [
            {"name": "p95", "status": "OK"},
            {"name": "errors", "status": "KO"},
        ],
    )

    summary = GatlingAssertionsReader().read(assertions_path)

    assert summary.total == 2
    assert summary.successful == 1
    assert summary.failed == 1


def test_rejects_assertion_without_status(tmp_path: Path) -> None:
    assertions_path = write_json(
        tmp_path / "assertions.json",
        [{"name": "p95"}],
    )

    with pytest.raises(ValueError, match="success field"):
        GatlingAssertionsReader().read(assertions_path)


def test_metrics_reader_includes_assertions(tmp_path: Path) -> None:
    metrics_path = write_json(
        tmp_path / "global_stats.json",
        {
            "numberOfRequests": {
                "total": 10,
                "ok": 10,
                "ko": 0,
            }
        },
    )
    assertions_path = write_json(
        tmp_path / "assertions.json",
        [{"name": "all requests succeeded", "passed": True}],
    )

    metrics = GatlingMetricsReader().read(
        metrics_path,
        assertions_path=assertions_path,
    )

    assert metrics.assertions is not None
    assert metrics.assertions.all_passed is True
    assert metrics.assertions.total == 1


def test_reads_gatling_result_boolean(tmp_path: Path) -> None:
    assertions_path = tmp_path / "assertions.json"
    assertions_path.write_text(
        """
[
  {
    "path": "Global",
    "target": "responseTime",
    "condition": "percentile3",
    "expectedValues": [2000.0],
    "result": true,
    "message": "Global: percentile3 of response time is less than 2000"
  },
  {
    "path": "Global",
    "target": "failedRequests",
    "condition": "percent",
    "expectedValues": [0.0],
    "result": false,
    "message": "Global: percentage of failed requests is 0"
  }
]
""".strip(),
        encoding="utf-8",
    )

    summary = GatlingAssertionsReader().read(assertions_path)

    assert summary.total == 2
    assert summary.successful == 1
    assert summary.failed == 1
    assert summary.all_passed is False
    assert summary.results[0].successful is True
    assert summary.results[1].successful is False
