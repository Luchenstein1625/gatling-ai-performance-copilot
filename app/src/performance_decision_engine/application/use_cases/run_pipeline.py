from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation


class NormalizationUseCase(Protocol):
    def execute(
        self,
        performance_path: Path,
        parameters_path: Path,
        results_path: Path,
        assertions_path: Path | None = None,
    ) -> NormalizedExecution: ...


class RecommendationUseCase(Protocol):
    def execute(self, execution: NormalizedExecution) -> Recommendation: ...


class DatasetUseCase(Protocol):
    fieldnames: tuple[str, ...]

    def execute(
        self,
        execution: NormalizedExecution,
        recommendation: Recommendation,
    ) -> dict[str, str | int | float | bool | None]: ...


@dataclass(frozen=True)
class PipelineResult:
    """In-memory result produced by the H10 local pipeline."""

    execution: NormalizedExecution
    recommendation: Recommendation
    dataset_row: dict[str, str | int | float | bool | None]
    dataset_fieldnames: tuple[str, ...]


class RunPipeline:
    """Integrate H5, H6 and H7 without duplicating their business rules."""

    def __init__(
        self,
        normalization: NormalizationUseCase,
        recommendation: RecommendationUseCase,
        dataset: DatasetUseCase,
    ) -> None:
        self._normalization = normalization
        self._recommendation = recommendation
        self._dataset = dataset

    def execute(
        self,
        performance_path: Path,
        parameters_path: Path,
        results_path: Path,
        assertions_path: Path | None = None,
    ) -> PipelineResult:
        execution = self._normalization.execute(
            performance_path=performance_path,
            parameters_path=parameters_path,
            results_path=results_path,
            assertions_path=assertions_path,
        )
        recommendation = self._recommendation.execute(execution)
        dataset_row = self._dataset.execute(execution, recommendation)

        return PipelineResult(
            execution=execution,
            recommendation=recommendation,
            dataset_row=dataset_row,
            dataset_fieldnames=self._dataset.fieldnames,
        )
