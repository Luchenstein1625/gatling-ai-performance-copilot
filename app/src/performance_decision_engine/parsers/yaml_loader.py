from pathlib import Path
from typing import Any

import yaml

from performance_decision_engine.core.exceptions import InputFileError


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise InputFileError(f"File not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise InputFileError(f"Invalid YAML file: {path}") from exc
    if not isinstance(data, dict):
        raise InputFileError(f"Expected a YAML object in: {path}")
    return data
