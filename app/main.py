# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.router.news_router import router as news_router
from app.router.scraper_router import router as scraper_router
from app.router.interpreter_router import router as interpreter_router

from app.core.setting import get_setting
from app.core.lifespan import lifespan

# Load settings
settings = get_setting()

# Initialize FastAPI app with lifespan context and settings
app = FastAPI(
    lifespan=lifespan,  # Lifespan management for startup and shutdown
    title="AI Information Broker",
    summary="A microservice for automated scraping, filtering, and processing of AI-related news from global sources.",
    openapi_url=settings.openapi_url,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,  
    allow_origins=["*"],  # Allow all origins (for development, tighten this in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include the router for application endpoints
app.include_router(news_router)
app.include_router(scraper_router)
app.include_router(interpreter_router)

# Health check route to verify service is running
@app.get("/", tags=["health"], summary="Check service health status")
async def health_check():
    return {
        "status": "running",
        "service": "ai-information-broker"
    }
