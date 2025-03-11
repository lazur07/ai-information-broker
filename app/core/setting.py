# app/core/settings.py
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from pathlib import Path

# settings
class Setting(BaseSettings):
    openapi_url: str | None = None  # OpenAPI
    docs_url: str | None = None  # Swagger UI
    redoc_url: str | None = None  # ReDoc UI

    gemini_api_key: str | None = None  # Gemini API key

    # Paths
    project_root: Path = Path(__file__).resolve().parent.parent  # Absolute project root
    assets_dir: Path = Path(__file__).parent.parent / "assets"  # Assets directory
    database_url: str | None = None  # Database URL

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    @model_validator(mode="before")
    def ensure_dirs_exist(cls, values):
        """Ensure directories exist when settings are loaded."""
        assets_dir = values.get("assets_dir")
        if assets_dir:
            assets_dir.mkdir(parents=True, exist_ok=True)
        return values


@lru_cache
def get_setting() -> Setting:
    return Setting()

settings = get_setting()
