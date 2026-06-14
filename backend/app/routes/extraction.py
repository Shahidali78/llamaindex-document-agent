"""Structured extraction, summarization, and comparison endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.extraction_schema import (
    CompareRequest,
    CompareResponse,
    ExtractRequest,
    ExtractResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from app.security import require_api_key
from app.services import document_service, extraction_service
from app.services.document_service import DocumentNotFoundError
from app.services.llamaindex_service import LlamaIndexNotConfiguredError
from app.utils.logger import get_logger

router = APIRouter(tags=["intelligence"])
logger = get_logger(__name__)


def _load_text(db: Session, document_id: str, owner_id: str):
    try:
        return document_service.load_text(db, document_id, owner_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _handle_llm_error(exc: Exception, action: str) -> HTTPException:
    if isinstance(exc, LlamaIndexNotConfiguredError):
        return HTTPException(status_code=503, detail=str(exc))
    logger.exception("%s failed", action)
    return HTTPException(status_code=500, detail=f"{action} failed: {exc}")


@router.post("/extract", response_model=ExtractResponse)
def extract(
    request: ExtractRequest,
    db: Session = Depends(get_db),
    owner_id: str = Depends(require_api_key),
) -> ExtractResponse:
    """Extract structured fields from a single document."""
    doc, text = _load_text(db, request.document_id, owner_id)
    try:
        result = extraction_service.extract_fields(text, doc.filename)
    except Exception as exc:  # noqa: BLE001
        raise _handle_llm_error(exc, "Extraction") from exc
    return ExtractResponse(document_id=doc.id, filename=doc.filename, extraction=result)


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(
    request: SummarizeRequest,
    db: Session = Depends(get_db),
    owner_id: str = Depends(require_api_key),
) -> SummarizeResponse:
    """Summarize a single document."""
    doc, text = _load_text(db, request.document_id, owner_id)
    try:
        summary = extraction_service.summarize(text, doc.filename, style=request.style)
    except Exception as exc:  # noqa: BLE001
        raise _handle_llm_error(exc, "Summarization") from exc
    return SummarizeResponse(document_id=doc.id, filename=doc.filename, summary=summary)


@router.post("/compare", response_model=CompareResponse)
def compare(
    request: CompareRequest,
    db: Session = Depends(get_db),
    owner_id: str = Depends(require_api_key),
) -> CompareResponse:
    """Compare two documents."""
    if request.document_id_a == request.document_id_b:
        raise HTTPException(status_code=400, detail="Provide two different document ids to compare.")
    doc_a, text_a = _load_text(db, request.document_id_a, owner_id)
    doc_b, text_b = _load_text(db, request.document_id_b, owner_id)
    try:
        comparison = extraction_service.compare(
            text_a, doc_a.filename, text_b, doc_b.filename, focus=request.focus
        )
    except Exception as exc:  # noqa: BLE001
        raise _handle_llm_error(exc, "Comparison") from exc
    return CompareResponse(
        document_id_a=doc_a.id,
        document_id_b=doc_b.id,
        filename_a=doc_a.filename,
        filename_b=doc_b.filename,
        comparison=comparison,
    )
