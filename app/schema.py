# schema.py
from pydantic import BaseModel, Field
from enum import Enum

# Define the NewsSource enum
class NewsSource(str, Enum):
    TECHCRUNCH = "techcrunch"
    KR36 = "36kr"



class InfoCollectReq(BaseModel):
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

class InfoCollectResp(BaseModel):
    """Response model for news scraping"""

    timestamp: str = Field(
        ..., description="Time of when the scraping was performed"
    )
    total_count: int = Field(..., description="Total number of news items found")
    items: list[NewsItem] = Field(..., description="list of scraped news items")


class ErrorResp(BaseModel):
    """Standard error response model"""

    status_code: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Error detail message")
