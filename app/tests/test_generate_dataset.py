from performance_decision_engine.application.use_cases.generate_dataset import (
    GenerateDatasetRow,
)
from performance_decision_engine.domain.entities.configuration import (
    EndpointConfiguration,
    PerformanceConfiguration,
    ResolvedTriplet,
)
from performance_decision_engine.domain.entities.execution import (
    AssertionResult,
    AssertionSummary,
    ExecutionMetrics,
    NormalizedExecution,
)
from performance_decision_engine.domain.entities.recommendation import Recommendation


def _execution(
    *,
    include_assertions: bool = True,
    second_endpoint_missing_values: bool = False,
) -> NormalizedExecution:
    assertions = None
    if include_assertions:
        assertions = AssertionSummary(
            total=1,
            successful=1,
            failed=0,
            all_passed=True,
            results=[AssertionResult(successful=True)],
        )

    second_concurrency = None if second_endpoint_missing_values else 20
    second_iterations = None if second_endpoint_missing_values else 40

    return NormalizedExecution(
        configuration=PerformanceConfiguration(
            load_type="sequence",
            endpoints=[
                EndpointConfiguration(
                    name="first",
                    feature_reference="classpath:first.feature",
                    enabled=True,
                    triplet=ResolvedTriplet(
                        concurrency_level="high",
                        concurrency_value=60,
                        iterations_level="high",
                        iterations_value=100,
                        response_time_level="high",
                        response_time_ms=3000,
                    ),
                ),
                EndpointConfiguration(
                    name="second",
                    feature_reference="classpath:second.feature",
                    enabled=True,
                    triplet=ResolvedTriplet(
                        concurrency_level="medium",
                        concurrency_value=second_concurrency,
                        iterations_level="medium",
                        iterations_value=second_iterations,
                        response_time_level="medium",
                        response_time_ms=2000,
                    ),
                ),
            ],
        ),
        global_metrics=ExecutionMetrics(
            total_requests=100,
            successful_requests=99,
            failed_requests=1,
            error_rate_percent=1.0,
            min_response_time_ms=10,
            mean_response_time_ms=200,
            max_response_time_ms=4000,
            p50_response_time_ms=150,
            p75_response_time_ms=250,
            p90_response_time_ms=500,
            p95_response_time_ms=1000,
            p99_response_time_ms=2500,
            requests_per_second=20.5,
            assertions=assertions,
        ),
        warnings=["global metrics"],
    )


def _recommendation() -> Recommendation:
    return Recommendation(
        action="review",
        explanation="Example",
        evidence={"metrics_scope": "execution"},
    )


def test_generates_stable_dataset_row() -> None:
    use_case = GenerateDatasetRow()

    row = use_case.execute(_execution(), _recommendation())

    assert tuple(row) == use_case.fieldnames
    assert row["schema_version"] == "1"
    assert row["metrics_scope"] == "execution"
    assert row["enabled_endpoint_count"] == 2
    assert row["configured_concurrency_total"] == 80
    assert row["configured_iterations_total"] == 140
    assert row["strictest_response_time_target_ms"] == 2000
    assert row["p95_response_time_ms"] == 1000
    assert row["assertions_failed"] == 0
    assert row["warning_count"] == 1
    assert row["recommendation_action"] == "review"


def test_does_not_invent_incomplete_aggregates() -> None:
    row = GenerateDatasetRow().execute(
        _execution(second_endpoint_missing_values=True),
        _recommendation(),
    )

    assert row["configured_concurrency_total"] is None
    assert row["configured_iterations_total"] is None
    assert row["strictest_response_time_target_ms"] == 2000


def test_preserves_missing_assertions_as_missing_values() -> None:
    row = GenerateDatasetRow().execute(
        _execution(include_assertions=False),
        _recommendation(),
    )

    assert row["assertions_total"] is None
    assert row["assertions_successful"] is None
    assert row["assertions_failed"] is None
    assert row["assertions_all_passed"] is None
