"""Self-service usage endpoint (per API key)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.usage_schema import UsageResponse
from app.security import require_api_key
from app.services import usage_service

router = APIRouter(tags=["usage"])


@router.get("/usage", response_model=UsageResponse)
def my_usage(
    db: Session = Depends(get_db),
    owner_id: str = Depends(require_api_key),
) -> UsageResponse:
    """Return the calling key's own usage counters."""
    stat = usage_service.get_or_create(db, owner_id)
    return UsageResponse(**usage_service.serialize(db, stat))
