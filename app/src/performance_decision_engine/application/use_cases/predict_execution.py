from pathlib import Path

from performance_decision_engine.application.use_cases.generate_dataset import (
    GenerateDatasetRow,
)
from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation
from performance_decision_engine.infrastructure.decision_tree_training_backend import (
    DecisionTreeTrainingBackend,
)


class PredictExecution:
    """Compare one H8 prediction with the deterministic H6 recommendation."""

    def __init__(self, backend: DecisionTreeTrainingBackend) -> None:
        self._backend = backend

    def execute(
        self,
        model_path: Path,
        execution: NormalizedExecution,
        rule_recommendation: Recommendation,
    ) -> dict[str, object]:
        row = GenerateDatasetRow().execute(execution, rule_recommendation)
        prediction = self._backend.predict(model_path, row)
        predicted_action = str(prediction["prediction"])
        return {
            "schema_version": "1",
            "model_role": "supervised_baseline_approximating_h6",
            **prediction,
            "rule_based_recommendation": rule_recommendation.action,
            "agreement": predicted_action == rule_recommendation.action,
            "limitations": [
                "The prediction approximates historical H6 labels.",
                "Human validation is required before changing a test quadrant.",
            ],
        }
