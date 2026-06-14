"""Document upload and retrieval endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.document_schema import (
    DocumentListResponse,
    DocumentResponse,
    UploadResponse,
)
from app.security import require_api_key
from app.services import document_service
from app.services.document_service import (
    DocumentNotFoundError,
    UnsupportedFileTypeError,
)
from app.services.llamaindex_service import llamaindex_service
from app.utils.logger import get_logger

router = APIRouter(prefix="/documents", tags=["documents"])
logger = get_logger(__name__)


@router.post("/upload", response_model=UploadResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    owner_id: str = Depends(require_api_key),
) -> UploadResponse:
    """Upload a PDF/TXT/DOCX file, store it, extract text, and index it."""
    try:
        stored_filename, path, size_bytes, ext = document_service.save_upload(file)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    text = document_service.extract_text(path, ext)
    doc = document_service.create_document(
        db,
        owner_id=owner_id,
        filename=file.filename or stored_filename,
        stored_filename=stored_filename,
        file_path=path,
        file_type=ext,
        size_bytes=size_bytes,
    )

    try:
        num_chunks = llamaindex_service.add_document(
            doc.id, doc.filename, text, owner_id
        )
        document_service.update_status(db, doc, status="indexed", num_chunks=num_chunks)
    except Exception as exc:  # noqa: BLE001 - surface indexing failure to client
        logger.exception("Indexing failed for document %s", doc.id)
        document_service.update_status(db, doc, status="failed", error=str(exc))
        raise HTTPException(status_code=502, detail=f"Document stored but indexing failed: {exc}") from exc

    return UploadResponse(
        message="Document uploaded and indexed successfully.",
        document=DocumentResponse.model_validate(doc),
    )


@router.get("", response_model=DocumentListResponse)
def list_documents(
    db: Session = Depends(get_db),
    owner_id: str = Depends(require_api_key),
) -> DocumentListResponse:
    """List the caller's uploaded documents."""
    docs = document_service.list_documents(db, owner_id)
    return DocumentListResponse(
        count=len(docs),
        documents=[DocumentResponse.model_validate(d) for d in docs],
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    owner_id: str = Depends(require_api_key),
) -> DocumentResponse:
    """Fetch metadata for one of the caller's documents."""
    try:
        doc = document_service.require_document(db, document_id, owner_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DocumentResponse.model_validate(doc)
