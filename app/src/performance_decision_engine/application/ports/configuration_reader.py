from pathlib import Path
from typing import Protocol

from performance_decision_engine.domain.entities.configuration import PerformanceConfiguration


class ConfigurationReader(Protocol):
    def read(self, performance_path: Path, parameters_path: Path) -> PerformanceConfiguration: ...
