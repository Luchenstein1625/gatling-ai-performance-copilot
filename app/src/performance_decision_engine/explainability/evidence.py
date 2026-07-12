from typing import Any


def build_evidence(**values: Any) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}
