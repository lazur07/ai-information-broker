# app/model/report_model.py
from sqlmodel import SQLModel, Field, Column, String
from typing import Optional
from datetime import datetime
from enum import Enum as PyEnum

class Report(SQLModel, table=True):
    id: int = Field(primary_key=True)
    timestamp: int
    title: str
    summary: str
    news_ids: list[str] = Field(sa_column=Column(String(1000)))  