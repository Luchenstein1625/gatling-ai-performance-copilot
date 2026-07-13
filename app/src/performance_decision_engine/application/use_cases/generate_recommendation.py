from performance_decision_engine.application.ports.recommendation_engine import (
    RecommendationEngine,
)
from performance_decision_engine.application.ports.recommendation_repository import (
    RecommendationRepository,
)
from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation


class GenerateRecommendation:
    def __init__(
        self,
        engine: RecommendationEngine,
        repository: RecommendationRepository | None = None,
    ) -> None:
        self._engine = engine
        self._repository = repository

    def execute(
        self,
        execution: NormalizedExecution,
        persist: bool = False,
    ) -> Recommendation:
        recommendation = self._engine.recommend(execution)
        if persist:
            if self._repository is None:
                raise ValueError("A recommendation repository is required when persist=True")
            self._repository.save(recommendation)
        return recommendation
