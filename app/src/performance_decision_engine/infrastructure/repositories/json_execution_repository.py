from pathlib import Path

from performance_decision_engine.application.ports.execution_repository import ExecutionRepository
from performance_decision_engine.domain.entities.execution import NormalizedExecution


class JsonExecutionRepository(ExecutionRepository):
    def save(self, execution: NormalizedExecution, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            execution.model_dump_json(indent=2),
            encoding="utf-8",
        )
