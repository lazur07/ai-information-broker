# app/router/scraper_router.py
from fastapi import APIRouter, Body, Path, Query, Depends, HTTPException
from app.service import InfoScraper, NewsManager, InfoInterpreter
from app.schema.scraper_schema import (
    ScrapeReq,
    ScrapeResp,
    ContentFetchReq,
    ContentFetchResp,
)
from app.core.setting import get_setting, Setting


router = APIRouter(
    prefix="/data/info",
    tags=["info"],
)


@router.post("/scrape", summary="Scrape AI-related news", response_model=ScrapeResp)
async def scrape_info(
    req: ScrapeReq = Body(...),
    scraper: InfoScraper = Depends(),
):
    return await scraper.scrape(req)

# fetch detailed news content: give a list of news IDs, return detailed news content
@router.post(
    "/fetch",
    summary="Fetch detailed news content",
    response_model=ContentFetchResp,
)
async def fetch_news_content(
    req: ContentFetchReq = Body(...),
    scraper: InfoScraper = Depends(),
):
    return await scraper.fetch_content(req)