from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from performance_decision_engine.infrastructure.parsers.yaml_loader import (
    InvalidInputFileError,
    load_yaml,
)

ParameterSection = Literal["concurrency", "iterations", "response_time"]


class UnknownParameterLevelError(ValueError):
    """Raised when a semantic level does not exist in the configuration."""


class ParameterValuesDocument(BaseModel):
    """Validated representation of parametricConfigurationValues.yaml."""

    model_config = ConfigDict(extra="allow")

    concurrency: dict[str, int] = Field(default_factory=dict)
    iterations: dict[str, int] = Field(default_factory=dict)
    response_time: dict[str, int] = Field(default_factory=dict)
    success_rate: float | int | None = None
    reasons: list[str] = Field(default_factory=list)


class ParameterValues:
    """Resolves semantic performance levels into numeric values."""

    def __init__(self, document: ParameterValuesDocument) -> None:
        self.document = document

    @classmethod
    def from_file(cls, path: Path) -> "ParameterValues":
        """Load and validate a parametric configuration YAML file."""
        raw = load_yaml(path)

        try:
            document = ParameterValuesDocument.model_validate(raw)
        except ValidationError as exc:
            raise InvalidInputFileError(
                f"Invalid parameter values document: {path}"
            ) from exc

        return cls(document)

    def resolve(
        self,
        section: ParameterSection,
        level: str,
        *,
        strict: bool = False,
    ) -> int | None:
        """
        Resolve a semantic level such as 'high' into its numeric value.

        When strict=False, unknown levels return None.
        When strict=True, UnknownParameterLevelError is raised.
        """
        normalized_level = level.strip().lower()
        values = self._section_values(section)
        value = values.get(normalized_level)

        if value is not None:
            return value

        if strict:
            available = ", ".join(sorted(values)) or "no levels configured"
            raise UnknownParameterLevelError(
                f"Unknown level '{level}' for section '{section}'. "
                f"Available levels: {available}"
            )

        return None

    def resolve_concurrency(self, level: str, *, strict: bool = False) -> int | None:
        return self.resolve("concurrency", level, strict=strict)

    def resolve_iterations(self, level: str, *, strict: bool = False) -> int | None:
        return self.resolve("iterations", level, strict=strict)

    def resolve_response_time(self, level: str, *, strict: bool = False) -> int | None:
        return self.resolve("response_time", level, strict=strict)

    @property
    def success_rate(self) -> float | int | None:
        return self.document.success_rate

    @property
    def reasons(self) -> tuple[str, ...]:
        return tuple(self.document.reasons)

    def _section_values(self, section: ParameterSection) -> dict[str, int]:
        return getattr(self.document, section)
