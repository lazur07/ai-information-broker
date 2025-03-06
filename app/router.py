# router.py
from fastapi import APIRouter, Body, Path, Query, Depends, HTTPException
from app.service import InfoScraper
from app.schema import InfoCollectReq, InfoCollectResp
from functools import lru_cache

router = APIRouter(
    prefix="/data/info",
    tags=["info"],
)

@lru_cache()
def get_info_scraper():
    return InfoScraper(headless=True)

@router.post(
    "/scrape", summary="Scrape AI-related news", response_model=InfoCollectResp
)
async def scrape_info(
    req: InfoCollectReq = Body(...),
    service: InfoScraper = Depends(get_info_scraper),
):
    return await service.scrape(req)