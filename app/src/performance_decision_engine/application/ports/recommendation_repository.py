from typing import Protocol

from performance_decision_engine.domain.entities.recommendation import Recommendation


class RecommendationRepository(Protocol):
    def save(self, recommendation: Recommendation) -> None: ...
