from pathlib import Path

from performance_decision_engine.application.use_cases.explain_model import (
    ExplainModel,
)


class FakeExplainabilityBackend:
    def __init__(self) -> None:
        self.calls: list[tuple[Path, Path]] = []

    def explain(
        self,
        model_path: Path,
        output_path: Path,
    ) -> dict[str, object]:
        self.calls.append((model_path, output_path))
        return {
            "schema_version": "1",
            "model_type": "DecisionTreeClassifier",
        }


def test_delegates_model_explanation_to_backend(tmp_path: Path) -> None:
    backend = FakeExplainabilityBackend()
    model = tmp_path / "model.joblib"
    output = tmp_path / "explanation.json"

    result = ExplainModel(backend).execute(model, output)

    assert backend.calls == [(model, output)]
    assert result == {
        "schema_version": "1",
        "model_type": "DecisionTreeClassifier",
    }
