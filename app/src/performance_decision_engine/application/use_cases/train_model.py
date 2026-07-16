from pathlib import Path
from typing import Protocol


class TrainingBackend(Protocol):
    """Port implemented by an infrastructure Machine Learning backend."""

    def train(
        self,
        dataset_path: Path,
        model_path: Path,
        report_path: Path,
    ) -> dict[str, object]:
        """Train, persist and report one supervised-learning baseline."""


class TrainModel:
    """Orchestrate H8 training without coupling the application to scikit-learn."""

    def __init__(self, backend: TrainingBackend) -> None:
        self._backend = backend

    def execute(
        self,
        dataset_path: Path,
        model_path: Path,
        report_path: Path,
    ) -> dict[str, object]:
        return self._backend.train(dataset_path, model_path, report_path)
