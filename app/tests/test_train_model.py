from pathlib import Path

from performance_decision_engine.application.use_cases.train_model import TrainModel


class FakeTrainingBackend:
    def __init__(self) -> None:
        self.received: tuple[Path, Path, Path] | None = None

    def train(
        self,
        dataset_path: Path,
        model_path: Path,
        report_path: Path,
    ) -> dict[str, object]:
        self.received = (dataset_path, model_path, report_path)
        return {"model_type": "fake"}


def test_train_model_delegates_to_backend() -> None:
    backend = FakeTrainingBackend()
    use_case = TrainModel(backend)

    result = use_case.execute(
        Path("dataset.csv"),
        Path("model.joblib"),
        Path("report.json"),
    )

    assert result == {"model_type": "fake"}
    assert backend.received == (
        Path("dataset.csv"),
        Path("model.joblib"),
        Path("report.json"),
    )
