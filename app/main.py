# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.router import router
from app.core import lifespan, get_setting
from app.schema import ErrorResp  

settings = get_setting()

app = FastAPI(
    lifespan=lifespan,
    title="AI Information Broker",
    summary="A microservice for automated scraping, filtering, and processing of AI-related news from global sources.",
    openapi_url=settings.openapi_url,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    responses={"400": {"model": ErrorResp}, "500": {"model": ErrorResp}},
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,  
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(router)

@app.get("/", tags=["health"], summary="Check service health status")
async def health_check():
    return {
        "status": "running",
        "service": "ai-information-broker"
    }