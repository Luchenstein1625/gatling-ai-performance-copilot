from abc import ABC, abstractmethod
from pathlib import Path

from performance_decision_engine.domain.entities.execution import ExecutionMetrics


class MetricsReader(ABC):
    @abstractmethod
    def read(
        self,
        path: Path,
        assertions_path: Path | None = None,
    ) -> ExecutionMetrics:
        """Read and normalize metrics from an external results source."""
        raise NotImplementedError
