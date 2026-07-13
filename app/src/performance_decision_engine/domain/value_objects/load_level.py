from enum import StrEnum


class LoadLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def parse(cls, value: str) -> "LoadLevel":
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            raise ValueError(f"Unsupported load level: {value!r}") from exc

    def next(self) -> "LoadLevel":
        if self is LoadLevel.LOW:
            return LoadLevel.MEDIUM
        if self is LoadLevel.MEDIUM:
            return LoadLevel.HIGH
        return LoadLevel.HIGH

    def previous(self) -> "LoadLevel":
        if self is LoadLevel.HIGH:
            return LoadLevel.MEDIUM
        if self is LoadLevel.MEDIUM:
            return LoadLevel.LOW
        return LoadLevel.LOW
