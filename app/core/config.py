from dataclasses import dataclass, field
import os


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    PROJECT_NAME: str = field(
        default_factory=lambda: os.getenv("APP_NAME", "Task Management API")
    )
    VERSION: str = field(default_factory=lambda: os.getenv("VERSION", "1.0.0"))
    DESCRIPTION: str = "Interview demo: FastAPI task management API"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "sqlite+aiosqlite:///./tasks.db",
        )
    )
    API_KEY: str = field(default_factory=lambda: os.getenv("API_KEY", "dev-secret"))
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    TESTING: bool = field(default_factory=lambda: _get_bool("TESTING", False))


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
