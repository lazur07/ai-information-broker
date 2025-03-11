# app/router/interpreter_router.py
from fastapi import APIRouter, Body, Path, Query, Depends, HTTPException
from app.service import InfoInterpreter
from app.schema.interpreter_schema import (
    InterpretReq,
    InterpretResp,
)
from app.core.setting import get_setting, Setting

router = APIRouter(
    prefix="/data/info",
    tags=["info"],
)


@router.post(
    "/report",
    summary="Generate a report from news data",
    response_model=InterpretResp,
)
async def generate_report(
    req: InterpretReq = Body(...),
    interpreter: InfoInterpreter = Depends(),
):
    """Generate a summarized report from a JSON file of news items using Gemini API."""
    return await interpreter.generate_report(req)
