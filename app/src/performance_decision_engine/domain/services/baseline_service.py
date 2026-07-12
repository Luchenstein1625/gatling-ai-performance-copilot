from performance_decision_engine.domain.entities.recommendation import Recommendation


def recommend_baseline(
    error_rate_percent: float,
    p95_response_time_ms: int | None,
    expected_response_time_ms: int | None,
) -> Recommendation:
    evidence = {
        "error_rate_percent": error_rate_percent,
        "p95_response_time_ms": p95_response_time_ms,
        "expected_response_time_ms": expected_response_time_ms,
    }

    if error_rate_percent > 0:
        return Recommendation(
            action="review",
            explanation="La ejecución presenta solicitudes fallidas.",
            evidence=evidence,
        )

    if (
        p95_response_time_ms is not None
        and expected_response_time_ms is not None
        and p95_response_time_ms > expected_response_time_ms
    ):
        return Recommendation(
            action="review",
            explanation="El p95 observado supera el tiempo esperado.",
            evidence=evidence,
        )

    return Recommendation(
        action="maintain",
        explanation="Las reglas básicas evaluadas no detectaron incumplimientos.",
        evidence=evidence,
    )
