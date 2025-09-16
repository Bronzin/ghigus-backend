"""Application configuration using Pydantic settings."""
from __future__ import annotations

import json
from typing import Any, List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings loaded from environment variables."""

    app_name: str = "Ghigus Backend"
    database_url: str = "sqlite:///./app.db"
    supabase_url: str | None = None
    supabase_service_key: str | None = None
    storage_bucket: str = "ghigus-files"
    allowed_origins: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: Any) -> List[str]:
        """Parse the allowed origins from JSON or comma separated strings."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return ["*"]
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return [item.strip() for item in value.split(",") if item.strip()]
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        return ["*"]


settings = Settings()
