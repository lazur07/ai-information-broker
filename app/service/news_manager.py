# app/service/news_manager.py
from typing import List

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
        
        # Convert SQLModel to dict, then to Pydantic model    
        news_dict = {
            "id": news.id,
            "url": news.url,
            "title": news.title,
            "author": news.author,
            "summary": news.summary,
            "content": news.content,
            "publish_timestamp": news.publish_timestamp,
            "gmt8time": news.gmt8time,
            "source": news.source,
            "is_interpreted": news.is_interpreted
        }
        return NewsItem(**news_dict)

    def list_news(self, req: NewsListReq) -> NewsListResp:
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
        
        # Convert SQLModel to Pydantic model using dictionary conversion
        pydantic_items = []
        for item in news_items:
            item_dict = {
                "id": item.id,
                "url": item.url,
                "title": item.title,
                "author": item.author,
                "summary": item.summary,
                "content": item.content,
                "publish_timestamp": item.publish_timestamp,
                "gmt8time": item.gmt8time,
                "source": item.source,
                "is_interpreted": item.is_interpreted
            }
            pydantic_items.append(NewsItem(**item_dict))
        
        # Return formatted response
        return NewsListResp(
            total_count=total_count,
            items=pydantic_items
        )