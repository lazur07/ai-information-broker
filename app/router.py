# app/router.py
from fastapi import APIRouter, Body, Path, Query, Depends, HTTPException
from app.service import InfoScraper, FileManager, InfoInterpreter
from app.schema import InfoCollectReq, InfoCollectResp, ReportGenerateReq, ReportGenerateResp
from app.core import get_setting, Setting


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


@router.get("/files", summary="list available JSON files", response_model=list[dict])
async def list_files(file_manager: FileManager = Depends()):
    """Returns a list of available JSON files in the assets directory with metadata."""
    return file_manager.list_files()


@router.get("/files/{filename}", summary="Download a specific JSON file")
async def download_file(filename: str, file_manager: FileManager = Depends()):
    """Download a specific JSON file from the assets directory."""
    return file_manager.get_file(filename)


@router.post(
    "/report", summary="Generate a report from news data", response_model=ReportGenerateResp
)
async def generate_report(
    req: ReportGenerateReq = Body(...),
    interpreter: InfoInterpreter = Depends(),
):
    """Generate a summarized report from a JSON file of news items using Gemini API."""
    return await interpreter.generate_report(req)