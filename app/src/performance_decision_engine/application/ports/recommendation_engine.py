from typing import Protocol

from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation


class RecommendationEngine(Protocol):
    def recommend(self, execution: NormalizedExecution) -> Recommendation: ...
