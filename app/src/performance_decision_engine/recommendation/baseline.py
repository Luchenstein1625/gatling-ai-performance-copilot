from pydantic import BaseModel


class BaselineRecommendation(BaseModel):
    action: str
    explanation: str


def recommend_from_global_metrics(
    error_rate: float,
    p95_ms: int | None,
    response_time_limit_ms: int | None,
) -> BaselineRecommendation:
    if error_rate > 0:
        return BaselineRecommendation(
            action="review",
            explanation="La ejecución contiene solicitudes fallidas.",
        )

    if (
        p95_ms is not None
        and response_time_limit_ms is not None
        and p95_ms > response_time_limit_ms
    ):
        return BaselineRecommendation(
            action="review",
            explanation="El p95 observado supera el límite esperado.",
        )

    return BaselineRecommendation(
        action="maintain",
        explanation="No se detectaron incumplimientos en las reglas básicas evaluadas.",
    )
