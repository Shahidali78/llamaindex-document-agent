"""Report generation endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.report_schema import ReportRequest, ReportResponse
from app.security import require_api_key
from app.services import document_service, extraction_service, report_service
from app.services.document_service import DocumentNotFoundError
from app.services.llamaindex_service import LlamaIndexNotConfiguredError
from app.utils.logger import get_logger

router = APIRouter(tags=["reports"])
logger = get_logger(__name__)


@router.post("/generate-report", response_model=ReportResponse)
def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    owner_id: str = Depends(require_api_key),
) -> ReportResponse:
    """Generate a markdown intelligence report for a document."""
    try:
        doc, text = document_service.load_text(db, request.document_id, owner_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    extraction = None
    summary = None
    try:
        if request.include_extraction:
            extraction = extraction_service.extract_fields(text, doc.filename)
        if request.include_summary:
            summary = extraction_service.summarize(text, doc.filename)
    except LlamaIndexNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Report generation failed")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}") from exc

    report_markdown = report_service.build_report(doc, extraction, summary)
    return ReportResponse(
        document_id=doc.id,
        filename=doc.filename,
        report_markdown=report_markdown,
        extraction=extraction,
        summary=summary,
    )
