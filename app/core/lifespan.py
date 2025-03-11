# app/core/lifespan.py
from fastapi import FastAPI
from loguru import logger
from app.core.database import init_db
from app.core.setting import get_setting
from fastapi.concurrency import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.add("logs/info.log", rotation="00:00", retention="7 days")
    logger.add("logs/error.log", rotation="00:00", retention="7 days", level="ERROR")
    logger.info("current setting: {}", get_setting())
    init_db()
    logger.info("[Service] Starting")
    yield
    logger.info("[Service] Shutting down")
