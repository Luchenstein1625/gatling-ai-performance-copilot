from performance_decision_engine.domain.entities.recommendation import Recommendation


class PlanQuadrantAction:
    """Translate a recommendation into an explicit, human-controlled next step."""

    def execute(
        self,
        recommendation: Recommendation,
        current_quadrant: int,
    ) -> dict[str, object]:
        if current_quadrant not in range(1, 10):
            raise ValueError("Current quadrant must be between 1 and 9.")

        if recommendation.action == "evolve":
            load_increase = recommendation.evidence.get(
                "proposed_load_increase_percent",
                10,
            )
            return {
                "schema_version": "1",
                "current_quadrant": current_quadrant,
                "action": "evaluate_load_increase",
                "proposed_quadrant": current_quadrant,
                "proposed_load_increase_percent": load_increase,
                "human_validation_required": True,
                "triggered_rule": recommendation.evidence.get("triggered_rule"),
                "explanation": (
                    f"Evaluate a controlled load increase of {load_increase}% "
                    "and let a specialist approve it."
                ),
            }

        review_required = recommendation.action == "review"
        return {
            "schema_version": "1",
            "current_quadrant": current_quadrant,
            "action": "review_configuration" if review_required else "maintain_configuration",
            "proposed_quadrant": current_quadrant,
            "human_validation_required": review_required,
            "triggered_rule": recommendation.evidence.get("triggered_rule"),
            "explanation": (
                "Review the configuration and let a specialist confirm a new quadrant."
                if review_required
                else "Keep the current quadrant; no rule breach was detected."
            ),
        }
