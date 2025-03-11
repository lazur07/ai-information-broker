# app/service/news_manager.py
from typing import List, Optional, Tuple

from fastapi import Depends, HTTPException
from loguru import logger
from sqlmodel import Session, select, and_, func

from app.core.database import get_session
from app.model.news_model import News
from app.schema.news_schema import NewsItem, NewsListReq, NewsListResp


class NewsManager:
    """Service for managing news items in the database for frontend display."""

    def __init__(self, db: Session = Depends(get_session)):
        self._db = db

    def get_news_by_id(self, news_id: str) -> NewsItem:
        """Get a single news item by ID."""
        logger.info(f"Fetching news with ID: {news_id}")
        news = self._db.exec(select(News).where(News.id == news_id)).first()
        
        if not news:
            logger.warning(f"News with ID {news_id} not found")
            raise HTTPException(status_code=404, detail=f"News item with ID {news_id} not found")
            
        return NewsItem.model_validate(news)

    def list_news(self, req: NewsListReq) -> NewsListResp:
        """
        List news items with pagination and filtering.
        Returns a NewsListResp with items and total count.
        """
        logger.info(f"Listing news with parameters: {req.model_dump()}")
        
        # Build the base query
        query = select(News)
        
        # Apply filters
        filters = []
        
        if req.source:
            filters.append(News.source == req.source)
            
        if req.start_date:
            # Convert datetime to timestamp
            start_timestamp = int(req.start_date.timestamp())
            filters.append(News.publish_timestamp >= start_timestamp)
            
        if req.end_date:
            # Convert datetime to timestamp
            end_timestamp = int(req.end_date.timestamp())
            filters.append(News.publish_timestamp <= end_timestamp)
            
        if req.category:
            # This assumes you might store category information somewhere in the article
            # You might need to adjust this based on your actual schema
            filters.append(News.title.contains(req.category) | News.summary.contains(req.category))
            
        # Apply all filters if any exist
        if filters:
            query = query.where(and_(*filters))
            
        # Get total count before applying pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_count = self._db.exec(count_query).one()
        
        # Apply sorting, newest first
        query = query.order_by(News.publish_timestamp.desc())
        
        # Apply pagination
        query = query.offset(req.offset).limit(req.limit)
        
        # Execute the query
        news_items = self._db.exec(query).all()
        logger.info(f"Found {len(news_items)} news items (total: {total_count})")
        
        # Convert to Pydantic models and return formatted response
        return NewsListResp(
            total_count=total_count,
            items=[NewsItem.model_validate(item) for item in news_items]
        )