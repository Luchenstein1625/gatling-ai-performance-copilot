import csv
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from performance_decision_engine.domain.entities.recommendation import Recommendation


class EvolutionObservation(BaseModel):
    """Comparable historical result for one component, ordered oldest to newest."""

    component_id: str = Field(min_length=1)
    recommendation_action: str
    p95_response_time_ms: int = Field(ge=0)
    response_time_target_ms: int = Field(gt=0)
    error_rate_percent: float = Field(ge=0.0, le=100.0)
    assertions_all_passed: bool


class EvaluateEvolution:
    """Promote a compliant result to evolve only when its history is stable."""

    def __init__(
        self,
        minimum_consecutive_successes: int = 3,
        maximum_sla_utilization: float = 0.70,
        proposed_load_increase_percent: int = 10,
    ) -> None:
        if minimum_consecutive_successes < 2:
            raise ValueError("At least two consecutive successes are required.")
        if not 0 < maximum_sla_utilization < 1:
            raise ValueError("SLA utilization must be between zero and one.")
        if proposed_load_increase_percent <= 0:
            raise ValueError("The proposed load increase must be positive.")

        self.minimum_consecutive_successes = minimum_consecutive_successes
        self.maximum_sla_utilization = maximum_sla_utilization
        self.proposed_load_increase_percent = proposed_load_increase_percent

    def execute(
        self,
        component_id: str,
        current_recommendation: Recommendation,
        history: list[EvolutionObservation],
    ) -> Recommendation:
        if current_recommendation.action != "maintain":
            return current_recommendation

        component_history = [
            observation for observation in history if observation.component_id == component_id
        ]
        recent = component_history[-self.minimum_consecutive_successes :]
        evidence = {
            **current_recommendation.evidence,
            "component_id": component_id,
            "required_consecutive_successes": self.minimum_consecutive_successes,
            "observed_comparable_executions": len(component_history),
            "maximum_sla_utilization": self.maximum_sla_utilization,
        }

        if len(recent) < self.minimum_consecutive_successes:
            evidence["evolution_reason"] = "insufficient_history"
            return Recommendation(
                action="maintain",
                explanation=(
                    "La ejecución cumple, pero aún no existe historial comparable "
                    "suficiente para proponer más carga."
                ),
                evidence=evidence,
            )

        stable = all(
            observation.recommendation_action == "maintain"
            and observation.error_rate_percent == 0
            and observation.assertions_all_passed
            and (
                observation.p95_response_time_ms / observation.response_time_target_ms
                <= self.maximum_sla_utilization
            )
            for observation in recent
        )
        if not stable:
            evidence["evolution_reason"] = "stability_criteria_not_met"
            return Recommendation(
                action="maintain",
                explanation=(
                    "La ejecución cumple, pero el historial reciente no conserva "
                    "el margen y la estabilidad exigidos para aumentar la carga."
                ),
                evidence=evidence,
            )

        evidence.update(
            {
                "triggered_rule": "stable_history",
                "consecutive_successes": len(recent),
                "sla_utilization": [
                    observation.p95_response_time_ms / observation.response_time_target_ms
                    for observation in recent
                ],
                "proposed_load_increase_percent": self.proposed_load_increase_percent,
            }
        )
        return Recommendation(
            action="evolve",
            explanation=(
                "El componente mantiene resultados estables y con margen; "
                "puede evaluarse un incremento controlado de carga."
            ),
            evidence=evidence,
        )


def load_evolution_history(path: Path) -> list[EvolutionObservation]:
    """Load and validate comparable observations from a UTF-8 CSV file."""
    try:
        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            if reader.fieldnames is None:
                raise ValueError("Evolution history CSV must include a header.")

            required = set(EvolutionObservation.model_fields)
            missing = sorted(required.difference(reader.fieldnames))
            if missing:
                raise ValueError(
                    "Evolution history CSV is missing required columns: " + ", ".join(missing)
                )

            observations: list[EvolutionObservation] = []
            for row_number, row in enumerate(reader, start=2):
                try:
                    observations.append(EvolutionObservation.model_validate(row))
                except ValidationError as exc:
                    raise ValueError(f"Invalid evolution history row {row_number}: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"Could not read evolution history: {path}") from exc

    return observations
