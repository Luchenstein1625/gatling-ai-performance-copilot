from pathlib import Path

from performance_decision_engine.application.use_cases.generate_recommendation import (
    GenerateRecommendation,
)
from performance_decision_engine.domain.entities.configuration import (
    EndpointConfiguration,
    PerformanceConfiguration,
    ResolvedTriplet,
)
from performance_decision_engine.domain.entities.execution import ExecutionMetrics, NormalizedExecution
from performance_decision_engine.domain.value_objects.recommendation_decision import (
    RecommendationDecision,
)
from performance_decision_engine.infrastructure.recommendation import (
    RuleBasedRecommendationEngine,
)
from performance_decision_engine.infrastructure.repositories.json_recommendation_repository import (
    JsonRecommendationRepository,
)


def build_execution(*, failed_requests: int = 0, p95: int = 900) -> NormalizedExecution:
    total_requests = 100
    return NormalizedExecution(
        configuration=PerformanceConfiguration(
            load_type="load",
            endpoints=[
                EndpointConfiguration(
                    name="customers",
                    feature_reference="customers.feature",
                    enabled=True,
                    triplet=ResolvedTriplet(
                        concurrency_level="medium",
                        concurrency_value=20,
                        iterations_level="medium",
                        iterations_value=10,
                        response_time_level="medium",
                        response_time_ms=1000,
                    ),
                )
            ],
        ),
        global_metrics=ExecutionMetrics(
            total_requests=total_requests,
            successful_requests=total_requests - failed_requests,
            failed_requests=failed_requests,
            error_rate_percent=failed_requests / total_requests * 100,
            p95_response_time_ms=p95,
            requests_per_second=15.0,
        ),
    )


def test_stable_execution_keeps_configuration() -> None:
    recommendation = RuleBasedRecommendationEngine().recommend(build_execution())
    assert recommendation.decision is RecommendationDecision.KEEP
    assert recommendation.endpoint_recommendations[0].proposed_triplet.concurrency_value == 20


def test_failed_requests_require_review() -> None:
    recommendation = RuleBasedRecommendationEngine().recommend(
        build_execution(failed_requests=2)
    )
    assert recommendation.decision is RecommendationDecision.REVIEW
    assert "ERROR_RATE_DETECTED" in [item.code for item in recommendation.evidence]


def test_response_time_above_target_requires_review() -> None:
    recommendation = RuleBasedRecommendationEngine().recommend(build_execution(p95=1200))
    assert recommendation.decision is RecommendationDecision.REVIEW
    assert "RESPONSE_TIME_ABOVE_TARGET" in [item.code for item in recommendation.evidence]


def test_zero_requests_are_insufficient_data() -> None:
    execution = build_execution()
    execution.global_metrics = ExecutionMetrics(
        total_requests=0,
        successful_requests=0,
        failed_requests=0,
        error_rate_percent=0.0,
    )
    recommendation = RuleBasedRecommendationEngine().recommend(execution)
    assert recommendation.decision is RecommendationDecision.INSUFFICIENT_DATA


def test_use_case_persists_recommendation(tmp_path: Path) -> None:
    output = tmp_path / "recommendation.json"
    use_case = GenerateRecommendation(
        engine=RuleBasedRecommendationEngine(),
        repository=JsonRecommendationRepository(output),
    )
    use_case.execute(build_execution(), persist=True)
    assert output.exists()
    assert '"decision": "keep"' in output.read_text(encoding="utf-8")
