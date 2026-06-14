"""Pydantic schemas for the chat / RAG endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question to answer from indexed docs")
    document_ids: list[str] | None = Field(
        default=None,
        description="Optional list of document ids to restrict retrieval to. None = all docs.",
    )
    top_k: int | None = Field(default=None, ge=1, le=20, description="Number of chunks to retrieve")


class SourceNode(BaseModel):
    document_id: str | None = None
    filename: str | None = None
    snippet: str
    score: float | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceNode]
