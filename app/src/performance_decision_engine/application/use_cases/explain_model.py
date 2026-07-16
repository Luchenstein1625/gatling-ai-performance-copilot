from pathlib import Path
from typing import Protocol


class ExplainabilityBackend(Protocol):
    """Port implemented by an infrastructure model-explanation backend."""

    def explain(
        self,
        model_path: Path,
        output_path: Path,
    ) -> dict[str, object]:
        """Explain one trusted H8 model artifact and persist the result."""


class ExplainModel:
    """Orchestrate H9 model explanation without coupling application to scikit-learn."""

    def __init__(self, backend: ExplainabilityBackend) -> None:
        self._backend = backend

    def execute(
        self,
        model_path: Path,
        output_path: Path,
    ) -> dict[str, object]:
        return self._backend.explain(model_path, output_path)
