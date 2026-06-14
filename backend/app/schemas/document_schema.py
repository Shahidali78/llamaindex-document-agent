"""Pydantic schemas for document endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    """Public representation of a stored document."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_type: str
    size_bytes: int
    num_chunks: int
    status: str
    error: str | None = None
    created_at: datetime


class DocumentListResponse(BaseModel):
    count: int
    documents: list[DocumentResponse]


class UploadResponse(BaseModel):
    message: str
    document: DocumentResponse
