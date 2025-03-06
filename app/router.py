# app/router.py
from fastapi import APIRouter, Body, Path, Query, Depends, HTTPException
from app.service import InfoScraper, FileManager
from app.schema import InfoCollectReq, InfoCollectResp
from app.core import get_setting, Setting
from functools import lru_cache
from typing import List, Dict

router = APIRouter(
    prefix="/data/info",
    tags=["info"],
)

@router.post(
    "/scrape", summary="Scrape AI-related news", response_model=InfoCollectResp
)
async def scrape_info(
    req: InfoCollectReq = Body(...),
    service: InfoScraper = Depends(),
):
    return await service.scrape(req)


@router.get("/files", summary="List available JSON files", response_model=List[Dict])
async def list_files(file_manager: FileManager = Depends()):
    """Returns a list of available JSON files in the assets directory with metadata."""
    return file_manager.list_files()


@router.get("/files/{filename}", summary="Download a specific JSON file")
async def download_file(filename: str, file_manager: FileManager = Depends()):
    """Download a specific JSON file from the assets directory."""
    return file_manager.get_file(filename)
