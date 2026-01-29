from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.scaffolds import router as scaffolds_router
from app.api.chat import router as chat_router
from app.db.database import init_db
from app.api import auth, saved_scaffolds
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0",
    description="REST API for bioprinting scaffold generation with LLM-assisted design",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scaffolds_router)
app.include_router(chat_router)
app.include_router(auth.router)
app.include_router(saved_scaffolds.router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting SHED backend API server")
    logger.info(f"App name: {settings.app_name}, Debug: {settings.debug}")
    init_db()
    logger.info("Database initialized successfully")


@app.get("/")
async def root():
    return {
        "message": "Bioprint Scaffold Generator API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "scaffolds": "/api/generate, /api/preview, /api/validate, /api/export/{id}, /api/presets",
            "chat": "/api/chat",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "debug": settings.debug,
    }
