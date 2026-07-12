from pathlib import Path
from typing import Protocol

from performance_decision_engine.domain.entities.execution import ExecutionMetrics


class MetricsReader(Protocol):
    def read(self, path: Path) -> ExecutionMetrics:
        ...
