# app/router/news_router.py
from fastapi import APIRouter, Body, Depends, Path

from app.schema.news_schema import NewsItem, NewsListReq, NewsListResp
from app.service import NewsManager

router = APIRouter(
    prefix="/data/info",
    tags=["info"],
)



@router.get(
    "/news/{news_id}",
    summary="Get detailed news content",
    response_model=NewsItem,
)
async def get_news(
    news_id: str = Path(..., description="Unique identifier for the news item"),
    news_manager: NewsManager = Depends(),
):
    """Get detailed content for a single news article."""
    return news_manager.get_news_by_id(news_id)

@router.post(
    "/news/list",
    summary="List news articles",
    response_model=NewsListResp,
)
async def list_news(
    req: NewsListReq = Body(...),
    news_manager: NewsManager = Depends(),
):
    return news_manager.list_news(req)