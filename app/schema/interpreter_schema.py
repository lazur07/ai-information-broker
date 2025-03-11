# app/schema/interpreter_schema.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class InterpretReq(BaseModel):
    """Request model for report generation"""
    
    item_ids: list[str] | None = Field(
        None, description="List of article IDs to include in the report. If provided, other filters are ignored."
    )
    category: str | None = Field(
        None, description="Filter by news category (e.g., 'AI')"
    )
    source: str | None = Field(
        None, description="Filter by news source (techcrunch or 36kr)"
    )
    limit: int = Field(
        default=10, description="Maximum number of news items to interpret"
    )
    start_date: datetime | None = Field(
        None, description="Start date filter (ISO 8601 format)"
    )
    end_date: datetime | None = Field(
        None, description="End date filter (ISO 8601 format)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_ids": ["kr36_3195608674008711", "tc_2976670"],
                "category": "AI",
                "limit": 10
            }
        }


class InterpretResp(BaseModel):
    """Response model for report generation"""
    
    timestamp: int = Field(..., description="Unix timestamp when the report was generated")
    title: str = Field(..., description="Title of the report")
    summary: str = Field(..., description="Summary of the report")
    key_points: List[str] = Field(..., description="Key points extracted from the news items")
    full_report: str = Field(..., description="Full text of the generated report")
    interpreted_count: int = Field(..., description="Number of news items interpreted")