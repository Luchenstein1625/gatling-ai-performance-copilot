from pathlib import Path
from typing import Any

from performance_decision_engine.parsers.yaml_loader import load_yaml


class ParameterResolver:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    @classmethod
    def from_file(cls, path: Path) -> "ParameterResolver":
        return cls(load_yaml(path))

    def resolve(self, section: str, level: str) -> int | float | None:
        value = self.data.get(section, {}).get(level)
        if isinstance(value, (int, float)):
            return value
        return None
