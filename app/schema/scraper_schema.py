# app/schema/scraper_schema.py
from pydantic import BaseModel, Field
from enum import Enum

from app.schema.news_schema import NewsItem, NewsSource

class ScrapeReq(BaseModel):
    """Request model for news scraping"""
    days_back: int = Field(
        default=1,
        description="Number of days to look back for news (default: 1 day). A value of 1 means 'yesterday', 2 means 'yesterday and the day before', etc."
    )
    category: str = Field(
        default="AI", 
        description="Category of news to scrape. Default is 'AI'."
    )
    source: list[str] = Field(
        default=["36kr", "techcrunch"],
        description="Sources to scrape news from. Options: 'techcrunch', '36kr', or both."
    )
    limit: int = Field(
        default=40, 
        description="Maximum number of news items to return."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "days_back": 1,
                "category": "AI",
                "source": ["36kr", "techcrunch"],
                "limit": 40
            }
        }

class ScrapeResp(BaseModel):
    """Response model for news scraping"""

    timestamp: str = Field(
        ..., description="Time of when the scraping was performed"
    )
    total_count: int = Field(..., description="Total number of news items found")
    items: list[NewsItem] = Field(..., description="list of scraped news items")

class ContentFetchReq(BaseModel):
    """Request model for fetching news content"""
    item_ids: list[str] = Field(
        ..., description="List of article IDs to fetch content for"
    )

class ContentFetchResp(ScrapeResp):
    pass
    