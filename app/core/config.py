# app/core/config.py
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # meta/app
    app_name: str = "Ghigus API"

    # CORS
    allowed_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://ghigus.it",
            "https://www.ghigus.it",
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
