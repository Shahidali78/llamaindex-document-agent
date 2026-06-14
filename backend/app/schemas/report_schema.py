"""Pydantic schemas for report generation."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.extraction_schema import ExtractionResult


class ReportRequest(BaseModel):
    document_id: str
    include_extraction: bool = Field(default=True)
    include_summary: bool = Field(default=True)


class ReportResponse(BaseModel):
    document_id: str
    filename: str
    report_markdown: str
    extraction: ExtractionResult | None = None
    summary: str | None = None
