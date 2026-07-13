from typing import Protocol

from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.value_objects.rule_evaluation import RuleEvaluation


class RecommendationRule(Protocol):
    def evaluate(self, execution: NormalizedExecution) -> RuleEvaluation: ...
