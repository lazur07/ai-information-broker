# app/schema/interpreter_schema.py
from pydantic import BaseModel, Field
from datetime import datetime

class InterpretReq(BaseModel):
    """Request model for report generation"""
    
    item_ids: list[str] | None = Field(
        None, description="list of article IDs to include in the report. If provided, other filters are ignored."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "item_ids": ["kr36_3195608674008711", "kr36_3195612465577606", "tc_2976670"],
                "filename": "20250306131136 - 20250307131136.json",
            }
        }


class InterpretResp(BaseModel):
    """Response model for report generation"""
    
    timestamp: int = Field(..., description="Unix timestamp when the report was generated")
    report_file: str = Field(..., description="Filename of the generated report")
    title: str = Field(..., description="Title of the report")
    summary: str = Field(..., description="Summary of the report")
    key_points: list[str] = Field(..., description="Key points extracted from the news items")
    full_report: str = Field(..., description="Full text of the generated report")
