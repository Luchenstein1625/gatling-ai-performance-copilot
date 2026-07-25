from performance_decision_engine.domain.entities.recommendation import Recommendation


class PlanQuadrantAction:
    """Translate maintain/review into an explicit, human-controlled next step."""

    def execute(
        self,
        recommendation: Recommendation,
        current_quadrant: int,
    ) -> dict[str, object]:
        if current_quadrant not in range(1, 10):
            raise ValueError("Current quadrant must be between 1 and 9.")

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
