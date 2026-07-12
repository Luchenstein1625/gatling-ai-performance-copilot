from pathlib import Path
from typing import Any

import yaml


class InvalidInputFileError(ValueError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise InvalidInputFileError(f"File not found: {path}")

    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise InvalidInputFileError(f"Invalid YAML file: {path}") from exc

    if not isinstance(value, dict):
        raise InvalidInputFileError(f"Expected YAML object: {path}")

    return value
