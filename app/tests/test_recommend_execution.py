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


def _rule_names(result: object) -> list[str]:
    evidence = getattr(result, "evidence")
    trace = evidence["decision_trace"]
    assert isinstance(trace, list)
    return [entry["rule"] for entry in trace]


def test_recommendation_maintains_when_execution_complies() -> None:
    result = RecommendExecution().execute(_execution())

    assert result.action == "maintain"
    assert result.explanation == "Las reglas básicas evaluadas no detectaron incumplimientos."
    assert result.evidence["metrics_scope"] == "execution"
    assert result.evidence["triggered_rule"] is None
    assert _rule_names(result) == [
        "enabled_endpoints",
        "total_requests",
        "assertions",
        "p95_available",
        "response_time_target_available",
        "error_rate",
        "p95_target",
    ]


def test_recommendation_reviews_failed_requests() -> None:
    result = RecommendExecution().execute(_execution(error_rate=1.0, failed_requests=1))

    assert result.action == "review"
    assert result.explanation == "La ejecución presenta solicitudes fallidas."
    assert result.evidence["failed_requests"] == 1
    assert result.evidence["triggered_rule"] == "error_rate"
    assert _rule_names(result)[-1] == "error_rate"


def test_recommendation_reviews_p95_above_target() -> None:
    result = RecommendExecution().execute(_execution(p95=4000, target=3000))

    assert result.action == "review"
    assert result.explanation == "El p95 observado supera el tiempo esperado."
    assert result.evidence["p95_response_time_ms"] == 4000
    assert result.evidence["expected_response_time_ms"] == 3000
    assert result.evidence["triggered_rule"] == "p95_target"
    assert _rule_names(result)[-1] == "p95_target"


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
    assert result.explanation == "Una o más assertions de la ejecución fallaron."
    assert result.evidence["failed_assertions"] == 1
    assert result.evidence["triggered_rule"] == "assertions"
    assert _rule_names(result) == [
        "enabled_endpoints",
        "total_requests",
        "assertions",
    ]


def test_recommendation_reviews_when_no_endpoint_is_enabled() -> None:
    result = RecommendExecution().execute(_execution(enabled=False))

    assert result.action == "review"
    assert result.explanation == (
        "No existen endpoints habilitados para generar una recomendación."
    )
    assert result.evidence["triggered_rule"] == "enabled_endpoints"
    assert _rule_names(result) == ["enabled_endpoints"]


def test_recommendation_reviews_empty_execution_with_trace() -> None:
    result = RecommendExecution().execute(_execution(total_requests=0))

    assert result.action == "review"
    assert result.evidence["triggered_rule"] == "total_requests"
    assert _rule_names(result) == ["enabled_endpoints", "total_requests"]


def test_recommendation_reviews_missing_p95_with_trace() -> None:
    result = RecommendExecution().execute(_execution(p95=None))

    assert result.action == "review"
    assert result.evidence["triggered_rule"] == "p95_available"
    assert _rule_names(result) == [
        "enabled_endpoints",
        "total_requests",
        "assertions",
        "p95_available",
    ]


def test_recommendation_reviews_missing_target_with_trace() -> None:
    result = RecommendExecution().execute(_execution(target=None))

    assert result.action == "review"
    assert result.evidence["triggered_rule"] == "response_time_target_available"
    assert _rule_names(result) == [
        "enabled_endpoints",
        "total_requests",
        "assertions",
        "p95_available",
        "response_time_target_available",
    ]


def test_trace_preserves_existing_evidence_fields() -> None:
    result = RecommendExecution().execute(_execution())

    assert result.evidence["total_requests"] == 100
    assert result.evidence["successful_requests"] == 100
    assert result.evidence["failed_requests"] == 0
    assert result.evidence["enabled_endpoints"] == ["example"]
    assert result.evidence["endpoint_response_time_targets_ms"] == {
        "example": 3000
    }
    assert result.evidence["warnings"] == []
