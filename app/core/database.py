# app/core/database.py
from sqlmodel import SQLModel, Session, create_engine
from app.core.setting import setting
from loguru import logger

# Create SQLModel engine
engine = create_engine(
    setting.database_url, echo=False, pool_size=5, max_overflow=10, pool_pre_ping=True
)


def init_db():
    """Create the tables in the database"""
    logger.info(f"Initializing database with URL: {setting.database_url}")
    from app.model.news_model import News
    from app.model.report_model import Report

    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session
