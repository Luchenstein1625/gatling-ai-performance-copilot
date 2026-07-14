from typing import TypeAlias

from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation

DatasetValue: TypeAlias = str | int | float | bool | None


class GenerateDatasetRow:
    """Build one stable dataset row from an execution and its H6 decision."""

    fieldnames: tuple[str, ...] = (
        "schema_version",
        "metrics_scope",
        "load_type",
        "enabled_endpoint_count",
        "configured_endpoint_target_count",
        "configured_concurrency_total",
        "configured_iterations_total",
        "strictest_response_time_target_ms",
        "total_requests",
        "successful_requests",
        "failed_requests",
        "error_rate_percent",
        "min_response_time_ms",
        "mean_response_time_ms",
        "max_response_time_ms",
        "p50_response_time_ms",
        "p75_response_time_ms",
        "p90_response_time_ms",
        "p95_response_time_ms",
        "p99_response_time_ms",
        "requests_per_second",
        "assertions_total",
        "assertions_successful",
        "assertions_failed",
        "assertions_all_passed",
        "warning_count",
        "recommendation_action",
    )

    def execute(
        self,
        execution: NormalizedExecution,
        recommendation: Recommendation,
    ) -> dict[str, DatasetValue]:
        enabled_endpoints = [
            endpoint for endpoint in execution.configuration.endpoints if endpoint.enabled
        ]
        concurrency_values = [
            endpoint.triplet.concurrency_value
            for endpoint in enabled_endpoints
            if endpoint.triplet.concurrency_value is not None
        ]
        iteration_values = [
            endpoint.triplet.iterations_value
            for endpoint in enabled_endpoints
            if endpoint.triplet.iterations_value is not None
        ]
        response_time_targets = [
            endpoint.triplet.response_time_ms
            for endpoint in enabled_endpoints
            if endpoint.triplet.response_time_ms is not None
        ]

        metrics = execution.global_metrics
        assertions = metrics.assertions

        row: dict[str, DatasetValue] = {
            "schema_version": "1",
            "metrics_scope": "execution",
            "load_type": execution.configuration.load_type,
            "enabled_endpoint_count": len(enabled_endpoints),
            "configured_endpoint_target_count": len(response_time_targets),
            "configured_concurrency_total": self._complete_sum(
                concurrency_values,
                expected_count=len(enabled_endpoints),
            ),
            "configured_iterations_total": self._complete_sum(
                iteration_values,
                expected_count=len(enabled_endpoints),
            ),
            "strictest_response_time_target_ms": (
                min(response_time_targets) if response_time_targets else None
            ),
            "total_requests": metrics.total_requests,
            "successful_requests": metrics.successful_requests,
            "failed_requests": metrics.failed_requests,
            "error_rate_percent": metrics.error_rate_percent,
            "min_response_time_ms": metrics.min_response_time_ms,
            "mean_response_time_ms": metrics.mean_response_time_ms,
            "max_response_time_ms": metrics.max_response_time_ms,
            "p50_response_time_ms": metrics.p50_response_time_ms,
            "p75_response_time_ms": metrics.p75_response_time_ms,
            "p90_response_time_ms": metrics.p90_response_time_ms,
            "p95_response_time_ms": metrics.p95_response_time_ms,
            "p99_response_time_ms": metrics.p99_response_time_ms,
            "requests_per_second": metrics.requests_per_second,
            "assertions_total": assertions.total if assertions is not None else None,
            "assertions_successful": (assertions.successful if assertions is not None else None),
            "assertions_failed": assertions.failed if assertions is not None else None,
            "assertions_all_passed": (assertions.all_passed if assertions is not None else None),
            "warning_count": len(execution.warnings),
            "recommendation_action": recommendation.action,
        }

        return row

    @staticmethod
    def _complete_sum(values: list[int], expected_count: int) -> int | None:
        if expected_count == 0 or len(values) != expected_count:
            return None
        return sum(values)
