"""API key management endpoints (admin-protected)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth_schema import (
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyResponse,
)
from app.schemas.usage_schema import UsageListResponse, UsageResponse
from app.security import require_admin
from app.services import auth_service, usage_service

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(require_admin)])


@router.post("/keys", response_model=ApiKeyCreatedResponse, status_code=201)
def create_key(body: ApiKeyCreate, db: Session = Depends(get_db)) -> ApiKeyCreatedResponse:
    """Mint a new API key. The plaintext key is returned only once."""
    record, plaintext = auth_service.create_api_key(db, body.name)
    return ApiKeyCreatedResponse(
        id=record.id,
        name=record.name,
        prefix=record.prefix,
        active=record.active,
        created_at=record.created_at,
        last_used_at=record.last_used_at,
        api_key=plaintext,
    )


@router.get("/keys", response_model=list[ApiKeyResponse])
def list_keys(db: Session = Depends(get_db)) -> list[ApiKeyResponse]:
    """List all API keys (metadata only — secrets are never returned)."""
    return [ApiKeyResponse.model_validate(k) for k in auth_service.list_api_keys(db)]


@router.delete("/keys/{key_id}")
def revoke_key(key_id: str, db: Session = Depends(get_db)) -> dict:
    """Revoke (deactivate) an API key."""
    if not auth_service.revoke_api_key(db, key_id):
        raise HTTPException(status_code=404, detail="API key not found.")
    return {"status": "revoked", "id": key_id}


@router.get("/usage", response_model=UsageListResponse)
def all_usage(db: Session = Depends(get_db)) -> UsageListResponse:
    """Usage across all owners, with managed-key labels resolved."""
    names = {k.id: k.name for k in auth_service.list_api_keys(db)}
    stats = usage_service.list_all(db)
    usage = [
        UsageResponse(**usage_service.serialize(db, stat, name=names.get(stat.owner_id)))
        for stat in stats
    ]
    return UsageListResponse(count=len(usage), usage=usage)
