"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Return basic service health and configuration status."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "openai_configured": bool(settings.openai_api_key),
        "auth_enabled": settings.auth_enabled,
    }
