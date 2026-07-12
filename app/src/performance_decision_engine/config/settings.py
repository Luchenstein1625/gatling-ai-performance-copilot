from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    log_level: str = os.getenv("PDE_LOG_LEVEL", "INFO")
    data_dir: str = os.getenv("PDE_DATA_DIR", "examples/output")


settings = Settings()
