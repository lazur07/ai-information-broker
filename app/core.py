# core.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from pathlib import Path

from loguru import logger
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager


# settings
class Setting(BaseSettings):
    openapi_url: str | None = None  # OpenAPI
    docs_url: str | None = None  # Swagger UI
    redoc_url: str | None = None  # ReDoc UI

    # Paths
    project_root: Path = Path(__file__).resolve().parent.parent  # Absolute project root
    assets_dir: Path = Path(__file__).parent.parent / "assets"  # Assets directory

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


# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.add("logs/info.log", rotation="00:00", retention="7 days")
    logger.add("logs/error.log", rotation="00:00", retention="7 days", level="ERROR")
    logger.info("current settings: {}", get_setting())

    logger.info("[Service] Starting")
    yield
    logger.info("[Service] Shutting down")
