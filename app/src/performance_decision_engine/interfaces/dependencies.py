from pathlib import Path

from performance_decision_engine.application.use_cases.generate_recommendation import (
    GenerateRecommendation,
)
from performance_decision_engine.infrastructure.recommendation import (
    RuleBasedRecommendationEngine,
)
from performance_decision_engine.infrastructure.repositories.json_recommendation_repository import (
    JsonRecommendationRepository,
)


def build_generate_recommendation(
    output_path: Path | None = None,
) -> GenerateRecommendation:
    repository = JsonRecommendationRepository(output_path) if output_path is not None else None
    return GenerateRecommendation(
        engine=RuleBasedRecommendationEngine(),
        repository=repository,
    )
