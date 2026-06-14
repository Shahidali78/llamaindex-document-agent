"""Pydantic schemas for API key management."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Human-readable label")


class ApiKeyResponse(BaseModel):
    """API key metadata (never includes the secret)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    prefix: str
    active: bool
    created_at: datetime
    last_used_at: datetime | None = None


class ApiKeyCreatedResponse(ApiKeyResponse):
    """Returned once at creation — includes the plaintext key."""

    api_key: str = Field(..., description="The secret key. Store it now; it is not shown again.")
