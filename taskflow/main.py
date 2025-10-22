"""FastAPI application entry point for TaskFlow."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from taskflow.api import api_router
from taskflow.models.base import init_db
from taskflow.utils.logger import get_logger
from taskflow.utils.config import settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events.

    Handles startup and shutdown events for the FastAPI application.

    Startup:
        - Initialize database tables using SQLAlchemy's create_all()
        - Note: This is development-only; production should use Alembic migrations

    Shutdown:
        - Clean up resources and log shutdown
    """
    # Startup
    logger.info("Starting TaskFlow application...")
    try:
        # Initialize database tables (creates tables if they don't exist)
        # This uses create_all() which is fine for development but should
        # be replaced with Alembic migrations for production
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Continue running even if DB init fails (tables might already exist)

    yield

    # Shutdown
    logger.info("Shutting down TaskFlow application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="TaskFlow - A demo task management SaaS with deliberate imperfections",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to TaskFlow API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "taskflow.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
