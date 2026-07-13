from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation
from performance_decision_engine.domain.services.baseline_service import recommend_execution


class RecommendExecution:
    """Generate a recommendation from the canonical normalized execution."""

    def execute(self, execution: NormalizedExecution) -> Recommendation:
        return recommend_execution(execution)
