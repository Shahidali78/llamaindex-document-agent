"""Pydantic schemas for usage tracking."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class UsageResponse(BaseModel):
    """Aggregated usage for a single owner."""

    owner_id: str
    name: str | None = None  # managed-key label, if the owner is a managed key
    total_requests: int
    uploads: int
    chats: int
    extractions: int
    summaries: int
    comparisons: int
    reports: int
    document_count: int
    created_at: datetime | None = None
    last_request_at: datetime | None = None


class UsageListResponse(BaseModel):
    count: int
    usage: list[UsageResponse]
