# app/schema/news_schema.py
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

from app.model.news_model import NewsSource

class NewsItem(BaseModel):
    """Model for a single news item"""

    id: str = Field(..., description="Unique identifier for the news item")
    url: str = Field(..., description="URL of the news article")
    title: str = Field(..., description="Title of the news article")
    author: str | None = Field(None, description="Author of the article")
    summary: str | None = Field(None, description="Summary or abstract of the article")
    content: str | None = Field(None, description="Full content of the article")
    publish_timestamp: int = Field(
        ..., description="Publication timestamp (Unix timestamp)"
    )
    gmt8time: str = Field(..., description="Formatted date/time in GMT+8 (China time)")
    source: NewsSource = Field(
        ..., description="Source of the news (techcrunch or 36kr)"
    ) 
    is_interpreted: bool = Field(
        ..., description="Flag indicating if the news item has been interpreted"
    )

class NewsListReq(BaseModel):
    limit: int = Field(
        default=10, description="Maximum number of news items to return"
    )
    offset: int = Field(
        default=0, description="Offset for pagination"
    )
    source: str | None = Field(
        None, description="Filter by news source (techcrunch or 36kr)"
    )
    category: str | None = Field(
        None, description="Filter by news category"
    )
    start_date: datetime | None = Field(
        None, description="Start date filter (ISO 8601 format, e.g., '2023-01-01T00:00:00')"
    )
    end_date: datetime | None = Field(
        None, description="End date filter (ISO 8601 format, e.g., '2023-12-31T23:59:59')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "limit": 10,
                "offset": 0,
                "source": "techcrunch",
                "category": "AI",
                "start_date": "2023-01-01T00:00:00",
                "end_date": "2023-12-31T23:59:59"
            }
        }

class NewsListResp(BaseModel):
    total_count: int = Field(..., description="Total number of news items")
    items: list[NewsItem] = Field(..., description="List of news items") 
