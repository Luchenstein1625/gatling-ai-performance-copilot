from pathlib import Path
from typing import Protocol

from performance_decision_engine.domain.entities.execution import NormalizedExecution


class ExecutionRepository(Protocol):
    def save(self, execution: NormalizedExecution, path: Path) -> None: ...
