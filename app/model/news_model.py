# app/model/news_model.py
from sqlmodel import SQLModel, Field, Column, String
from typing import Optional
from datetime import datetime
from enum import Enum as PyEnum


class NewsSource(str, PyEnum):
    """Enum for news sources"""
    TECHCRUNCH = "techcrunch"
    KR36 = "36kr"


class News(SQLModel, table=True):
    """News item model for database storage"""
    
    __tablename__ = "news"
    
    # Primary key using the original ID from sources
    id: str = Field(primary_key=True)
    
    # URL and basic article info
    url: str = Field(index=True)
    title: str
    author: str | None = Field(default=None)
    summary: str | None = Field(default=None)
    content: str | None = Field(default=None, sa_column=Column(String(65535), nullable=True))
    
    # Timestamps
    publish_timestamp: int = Field(index=True)
    gmt8time: str
    
    # Source information
    source: NewsSource
    
    # Interpretation content (replacing is_interpreted)
    interpretation: str | None = Field(default=None, sa_column=Column(String(65535), nullable=True))