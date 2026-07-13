from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation
from performance_decision_engine.domain.services.recommendation_service import (
    RecommendationService,
)
from performance_decision_engine.domain.services.rules import (
    AssertionRule,
    ErrorRateRule,
    ExecutionDataRule,
    ResponseTimeRule,
    StableExecutionRule,
)


class RuleBasedRecommendationEngine:
    def __init__(self, service: RecommendationService | None = None) -> None:
        self._service = service or RecommendationService(
            rules=(
                ExecutionDataRule(),
                AssertionRule(),
                ErrorRateRule(),
                ResponseTimeRule(),
                StableExecutionRule(),
            )
        )

    def recommend(self, execution: NormalizedExecution) -> Recommendation:
        return self._service.recommend(execution)
