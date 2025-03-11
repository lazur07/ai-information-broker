# app/service/info_interpreter.py
import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import aiohttp
import pytz
from fastapi import Depends, HTTPException
from loguru import logger
from sqlmodel import Session, select, or_, and_, update
from pathlib import Path

from google import genai
from google.genai import types

from app.core.database import get_session
from app.core.setting import Setting, get_setting
from app.model.news_model import News, NewsSource
from app.schema.news_schema import NewsItem
from app.schema.interpreter_schema import InterpretReq, InterpretResp
from app.service.news_manager import NewsManager


class InfoInterpreter:
    """Service for interpreting news and generating reports using Gemini API."""

    def __init__(
        self,
        db: Session = Depends(get_session),
        settings: Setting = Depends(get_setting),
    ):
        self._db = db
        self._settings = settings
        self._china_tz = pytz.timezone("Asia/Shanghai")
        self._gemini_client = genai.Client(api_key=settings.gemini_api_key)
        self._prompt_template = self._load_prompt_template()
        self._max_concurrent_requests = 5  # Limit concurrent requests to Gemini API

    def _load_prompt_template(self) -> str:
        """Load the prompt template from file."""
        prompt_path = Path(self._settings.project_root) / "prompt" / "interpret.txt"
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load prompt template: {e}")
            # Fallback to a basic prompt if file loading fails
            return "<system_prompt>Summarize the following content in Chinese.</system_prompt>"

    async def generate_report(self, req: InterpretReq) -> InterpretResp:
        """Generate a report from news data."""
        logger.info(f"Generating report with parameters: {req.model_dump()}")
        
        # If request has empty item_ids list, fetch latest 20 news items
        if req.item_ids is not None and len(req.item_ids) == 0:
            logger.info("Empty item_ids list provided, fetching latest 20 news items")
            query = select(News).order_by(News.publish_timestamp.desc()).limit(20)
            news_items = self._db.exec(query).all()
        else:
            # Get news items based on request filters
            news_items = self._get_news_items(req)
            
        if not news_items:
            raise HTTPException(status_code=404, detail="No news items found matching the criteria")
        
        logger.info(f"Found {len(news_items)} news items for interpretation")
        
        # Interpret news items that don't have interpretation yet
        items_to_interpret = [item for item in news_items if not item.interpretation]
        if items_to_interpret:
            logger.info(f"Interpreting {len(items_to_interpret)} news items")
            await self._interpret_news_items(items_to_interpret)
            
            # Refresh news items from database to get updated interpretations
            if req.item_ids is not None and len(req.item_ids) == 0:
                query = select(News).where(News.id.in_([item.id for item in news_items]))
                news_items = self._db.exec(query).all()
            else:
                news_items = self._get_news_items(req)
        
        # Generate the report
        report = self._generate_full_report(news_items)
        
        current_time = int(datetime.now().timestamp())
        return InterpretResp(
            timestamp=current_time,
            title=report["title"],
            summary=report["summary"],
            key_points=report["key_points"],
            full_report=report["full_text"],
            interpreted_count=len(news_items)
        )

    def _get_news_items(self, req: InterpretReq) -> List[News]:
        """Get news items based on request filters."""
        if req.item_ids:
            # If specific item IDs are provided, use them
            query = select(News).where(News.id.in_(req.item_ids))
        else:
            # Otherwise, apply filters
            query = select(News)
            filters = []
            
            if req.source:
                filters.append(News.source == req.source)
                
            if req.category:
                # This is a simplification - assumes category is in title or summary
                filters.append(News.title.contains(req.category) | News.summary.contains(req.category))
                
            if req.start_date:
                # Convert datetime to timestamp
                start_timestamp = int(req.start_date.timestamp())
                filters.append(News.publish_timestamp >= start_timestamp)
                
            if req.end_date:
                # Convert datetime to timestamp
                end_timestamp = int(req.end_date.timestamp())
                filters.append(News.publish_timestamp <= end_timestamp)
                
            # Apply all filters if any exist
            if filters:
                query = query.where(and_(*filters))
            
            # Sort by publish timestamp, newest first
            query = query.order_by(News.publish_timestamp.desc())
            
            # Apply limit
            query = query.limit(req.limit)
        
        # Execute the query
        news_items = self._db.exec(query).all()
        return news_items

    async def _interpret_news_items(self, news_items: List[News]) -> None:
        """Interpret multiple news items in parallel using Gemini API."""
        semaphore = asyncio.Semaphore(self._max_concurrent_requests)
        
        # Create tasks for each news item
        tasks = []
        for item in news_items:
            task = self._interpret_with_semaphore(semaphore, item)
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        # Commit all changes to the database
        self._db.commit()

    async def _interpret_with_semaphore(self, semaphore: asyncio.Semaphore, news_item: News) -> None:
        """Use a semaphore to limit concurrent API calls."""
        async with semaphore:
            interpretation = await self._interpret_news_item(news_item)
            if interpretation:
                news_item.interpretation = interpretation
                self._db.add(news_item)

    async def _interpret_news_item(self, news_item: News) -> Optional[str]:
        """Interpret a single news item using Gemini API."""
        if not news_item.content:
            logger.warning(f"News item {news_item.id} has no content to interpret")
            return None

        try:
            # Prepare the prompt with the news content
            prompt_with_context = self._prompt_template.replace("{{context}}", news_item.content)
            
            # Call Gemini API using the correct method
            response = await asyncio.to_thread(
                self._gemini_client.models.generate_content,
                model="gemini-2.0-flash",
                contents=prompt_with_context,
                config=types.GenerateContentConfig(
                    max_output_tokens=4096,
                    temperature=0.3
                )
            )
            
            if response.text:
                logger.info(f"Successfully interpreted news item {news_item.id}")
                return response.text
            
            logger.warning(f"Empty response from Gemini API for {news_item.id}")
            return None
            
        except Exception as e:
            logger.error(f"Error interpreting news item {news_item.id}: {e}")
            return None

    def _generate_full_report(self, news_items: List[News]) -> Dict[str, Any]:
        """Generate a full report from interpreted news items."""
        # Get current date in Beijing time
        now = datetime.now(self._china_tz)
        date_str = now.strftime("%Y年%m月%d日")
        
        # Generate title
        title = f"🌐 AI 每日速递 |📅 人工智能期刊{date_str} | 汇总 | 最新人工智能动态 🚀"
        
        # Estimate reading time (approximate)
        total_chars = sum(len(item.interpretation or "") for item in news_items)
        min_minutes = max(1, total_chars // 2000)  # Rough estimate: 2000 chars per minute
        max_minutes = max(2, total_chars // 1000)  # Slower reading: 1000 chars per minute
        reading_time = f"{min_minutes}~{max_minutes}"
        
        # Generate content summary
        summary = f"预计阅读时间:{reading_time}分钟"
        
        # Generate table of contents
        toc = ["📑 目录"]
        for i, item in enumerate(news_items, 1):
            # Generate an emoji based on the content theme
            emoji = self._get_emoji_for_content(item.title, item.content)
            toc.append(f"{i}. {emoji} {item.title}")
        
        # Generate full content
        content_parts = []
        for i, item in enumerate(news_items, 1):
            if item.interpretation:
                content_parts.append(f"{i}、{item.title}\n\n{item.interpretation}")
            else:
                # Fallback if no interpretation is available
                content_parts.append(f"{i}、{item.title}\n\n- 摘要: {item.summary or '无摘要可用'}")
        
        # Combine all parts
        full_text = f"{title}({summary})\n\n"
        full_text += "\n".join(toc) + "\n\n"
        full_text += "\n\n".join(content_parts)
        
        # Extract key points from all interpretations
        key_points = []
        for item in news_items:
            if item.interpretation:
                # Try to extract key points from the interpretation
                try:
                    # Look for the "关键点:" section in the interpretation
                    kp_section = item.interpretation.split("关键点:")[1].strip() if "关键点:" in item.interpretation else ""
                    if kp_section:
                        # Extract numbered points
                        points = [p.strip() for p in kp_section.split("\n") if p.strip() and any(f"{n})" in p for n in range(1, 10))]
                        key_points.extend(points)
                except Exception as e:
                    logger.warning(f"Error extracting key points from {item.id}: {e}")
        
        return {
            "title": title,
            "summary": summary,
            "key_points": key_points[:7],  # Limit to top 20 key points
            "full_text": full_text
        }

    def _get_emoji_for_content(self, title: str, content: Optional[str]) -> str:
        """Select an appropriate emoji based on content."""
        # Default emoji
        default_emoji = "🔍"
        
        # List of keywords and corresponding emojis
        keyword_emojis = {
            "fund": "💰", "investment": "💰", "融资": "💰", "funding": "💰", "million": "💰", "billion": "💰",
            "研究": "🔬", "research": "🔬", "study": "🔬", "discover": "🔬",
            "launch": "🚀", "发布": "🚀", "release": "🚀", "announce": "🚀",
            "partner": "🤝", "合作": "🤝", "collaborate": "🤝",
            "robot": "🤖", "机器人": "🤖",
            "security": "🔒", "安全": "🔒", "privacy": "🔒", "隐私": "🔒",
            "cloud": "☁️", "云": "☁️",
            "game": "🎮", "gaming": "🎮", "游戏": "🎮",
            "health": "🏥", "healthcare": "🏥", "医疗": "🏥", "health": "🏥",
            "education": "🎓", "learning": "🎓", "教育": "🎓", "学习": "🎓",
            "chip": "🔧", "hardware": "🔧", "芯片": "🔧", "硬件": "🔧",
            "policy": "📜", "regulation": "📜", "政策": "📜", "法规": "📜",
            "job": "💼", "career": "💼", "工作": "💼", "就业": "💼"
        }
        
        combined_text = (title + " " + (content or "")).lower()
        
        for keyword, emoji in keyword_emojis.items():
            if keyword.lower() in combined_text:
                return emoji
                
        return default_emoji