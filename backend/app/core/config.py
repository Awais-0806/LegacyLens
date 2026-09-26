from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "LegacyLens"
    app_env: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    max_request_body_bytes: int = 1_048_576
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    max_repository_size_mb: int = 100
    max_file_size_mb: int = 10
    max_file_count: int = 10000
    max_extraction_files: int = 10000
    ingestion_timeout_seconds: int = 30
    max_total_extracted_size_mb: int = 250
    max_path_length: int = 512

    database_url: str = "postgresql+psycopg://legacylens:change-me@localhost:5432/legacylens"
    sqlite_database_url: str = "sqlite:///./legacylens.db"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
