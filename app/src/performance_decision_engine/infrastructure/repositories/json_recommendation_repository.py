import json
from pathlib import Path

from performance_decision_engine.domain.entities.recommendation import Recommendation


class JsonRecommendationRepository:
    def __init__(self, output_path: Path) -> None:
        self._output_path = output_path

    def save(self, recommendation: Recommendation) -> None:
        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._output_path.with_suffix(f"{self._output_path.suffix}.tmp")
        payload = recommendation.model_dump(mode="json")
        temporary_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(self._output_path)
