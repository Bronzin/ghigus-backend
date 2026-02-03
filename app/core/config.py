# app/core/config.py
import secrets
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # meta/app
    app_name: str = "Ghigus API"

    # JWT Auth
    jwt_secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        alias="JWT_SECRET_KEY"
    )
    jwt_expire_minutes: int = Field(10080, alias="JWT_EXPIRE_MINUTES")  # 7 days
    rate_limit_login: str = Field("5/minute", alias="RATE_LIMIT_LOGIN")

    # CORS
    allowed_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://ghigus.com",
            "https://www.ghigus.com",
        ]
    )

    # DB & Supabase  (campi python in minuscolo, ENV alias MAIUSCOLI)
    database_url: str = Field(..., alias="DATABASE_URL")
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_service_key: str = Field(..., alias="SUPABASE_SERVICE_KEY")
    storage_bucket: str = Field("ghigus-files", alias="STORAGE_BUCKET")

    # CNC PowerPoint generation
    cnc_use_mock: bool = Field(True, alias="CNC_USE_MOCK")
    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        populate_by_name=True,   # usa gli alias MAIUSCOLI
        extra="ignore",          # ignora chiavi extra nel .env
    )

settings = Settings()
