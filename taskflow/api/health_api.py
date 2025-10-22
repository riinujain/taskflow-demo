"""Health check API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from taskflow.models.base import get_db_session

router = APIRouter()


@router.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "TaskFlow",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/db")
def database_health_check(db: Session = Depends(get_db_session)):
    """Check database connectivity."""
    try:
        # Simple query to test DB connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/ping")
def ping():
    """Simple ping endpoint."""
    return {"message": "pong"}
