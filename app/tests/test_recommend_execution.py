from performance_decision_engine.application.use_cases.recommend_execution import (
    RecommendExecution,
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


def _execution(
    *,
    error_rate: float = 0.0,
    failed_requests: int = 0,
    p95: int | None = 1000,
    target: int | None = 3000,
    total_requests: int = 100,
    enabled: bool = True,
    assertions: AssertionSummary | None = None,
) -> NormalizedExecution:
    return NormalizedExecution(
        configuration=PerformanceConfiguration(
            load_type="sequence",
            endpoints=[
                EndpointConfiguration(
                    name="example",
                    feature_reference="classpath:example.feature",
                    enabled=enabled,
                    triplet=ResolvedTriplet(
                        concurrency_level="high",
                        concurrency_value=60,
                        iterations_level="high",
                        iterations_value=10,
                        response_time_level="very_high",
                        response_time_ms=target,
                    ),
                )
            ],
        ),
        global_metrics=ExecutionMetrics(
            total_requests=total_requests,
            successful_requests=total_requests - failed_requests,
            failed_requests=failed_requests,
            error_rate_percent=error_rate,
            p95_response_time_ms=p95,
            assertions=assertions,
        ),
    )


def test_recommendation_maintains_when_execution_complies() -> None:
    result = RecommendExecution().execute(_execution())

    assert result.action == "maintain"
    assert result.evidence["metrics_scope"] == "execution"


def test_recommendation_reviews_failed_requests() -> None:
    result = RecommendExecution().execute(
        _execution(error_rate=1.0, failed_requests=1)
    )

    assert result.action == "review"


def test_recommendation_reviews_p95_above_target() -> None:
    result = RecommendExecution().execute(_execution(p95=4000, target=3000))

    assert result.action == "review"


def test_recommendation_reviews_failed_assertions() -> None:
    assertions = AssertionSummary(
        total=1,
        successful=0,
        failed=1,
        all_passed=False,
        results=[AssertionResult(successful=False)],
    )

    result = RecommendExecution().execute(_execution(assertions=assertions))

    assert result.action == "review"
    assert result.evidence["failed_assertions"] == 1


def test_recommendation_reviews_when_no_endpoint_is_enabled() -> None:
    result = RecommendExecution().execute(_execution(enabled=False))

    assert result.action == "review"
