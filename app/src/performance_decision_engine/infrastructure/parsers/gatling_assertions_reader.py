import json
from pathlib import Path
from typing import Any

from performance_decision_engine.domain.entities.execution import (
    AssertionResult,
    AssertionSummary,
)


class GatlingAssertionsReader:
    """Read and normalize Gatling assertions.json documents."""

    def read(self, path: Path) -> AssertionSummary:
        raw = self._load_json(path)
        assertion_items = self._extract_assertion_items(raw)
        results = [self._normalize_assertion(item) for item in assertion_items]

        successful = sum(result.successful for result in results)
        failed = len(results) - successful

        return AssertionSummary(
            total=len(results),
            successful=successful,
            failed=failed,
            all_passed=failed == 0,
            results=results,
        )

    @staticmethod
    def _load_json(path: Path) -> Any:
        if not path.exists():
            raise ValueError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as exc:
            raise ValueError(f"File is not valid UTF-8: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON file: {path}") from exc

    @classmethod
    def _extract_assertion_items(cls, raw: Any) -> list[dict[str, Any]]:
        if isinstance(raw, list):
            return cls._ensure_dict_items(raw)

        if not isinstance(raw, dict):
            raise ValueError("Invalid assertions document: expected an object or list")

        for key in ("assertions", "results"):
            value = raw.get(key)
            if isinstance(value, list):
                return cls._ensure_dict_items(value)

        # Some Gatling exporters use a dictionary keyed by assertion name.
        if raw and all(isinstance(value, dict) for value in raw.values()):
            return [
                {"name": str(name), **value}
                for name, value in raw.items()
                if isinstance(value, dict)
            ]

        if not raw:
            return []

        raise ValueError("Invalid assertions document: no assertions collection was found")

    @staticmethod
    def _ensure_dict_items(items: list[Any]) -> list[dict[str, Any]]:
        if not all(isinstance(item, dict) for item in items):
            raise ValueError("Invalid assertions document: every assertion must be an object")
        return items

    @classmethod
    def _normalize_assertion(cls, item: dict[str, Any]) -> AssertionResult:
        successful = cls._resolve_success(item)

        return AssertionResult(
            path=cls._optional_text(item, "path", "scope", "name"),
            target=cls._optional_text(item, "target", "metric"),
            condition=cls._optional_text(item, "condition", "operator"),
            expected=cls._first_present(item, "expected", "expectedValue"),
            actual=cls._first_present(item, "actual", "actualValue"),
            successful=successful,
            message=cls._optional_text(item, "message", "description", "error"),
        )

    @staticmethod
    def _resolve_success(item: dict[str, Any]) -> bool:
        for key in ("successful", "success", "passed", "valid"):
            value = item.get(key)
            if isinstance(value, bool):
                return value

        status = item.get("status")
        if isinstance(status, str):
            normalized = status.strip().lower()
            if normalized in {"ok", "pass", "passed", "success", "successful", "true"}:
                return True
            if normalized in {"ko", "fail", "failed", "failure", "false", "error"}:
                return False

        raise ValueError(
            "Invalid assertion: a boolean success field or recognized status is required"
        )

    @staticmethod
    def _first_present(
        item: dict[str, Any],
        *keys: str,
    ) -> str | int | float | bool | None:
        for key in keys:
            value = item.get(key)
            if isinstance(value, (str, int, float, bool)):
                return value
        return None

    @staticmethod
    def _optional_text(item: dict[str, Any], *keys: str) -> str | None:
        for key in keys:
            value = item.get(key)
            if value is not None:
                return str(value)
        return None
