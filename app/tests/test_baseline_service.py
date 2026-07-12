from performance_decision_engine.domain.services.baseline_service import recommend_baseline


def test_baseline_maintains_when_metrics_comply() -> None:
    result = recommend_baseline(
        error_rate_percent=0.0,
        p95_response_time_ms=1000,
        expected_response_time_ms=3000,
    )
    assert result.action == "maintain"


def test_baseline_reviews_when_errors_exist() -> None:
    result = recommend_baseline(
        error_rate_percent=1.0,
        p95_response_time_ms=1000,
        expected_response_time_ms=3000,
    )
    assert result.action == "review"
