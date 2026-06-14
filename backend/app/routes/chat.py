"""Chat / RAG endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.security import require_api_key
from app.services import document_service
from app.services.document_service import DocumentNotFoundError
from app.services.llamaindex_service import (
    LlamaIndexNotConfiguredError,
    llamaindex_service,
)
from app.utils.logger import get_logger

router = APIRouter(tags=["chat"])
logger = get_logger(__name__)


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    owner_id: str = Depends(require_api_key),
) -> ChatResponse:
    """Answer a question from the caller's documents with source citations."""
    # Validate that any requested documents belong to the caller.
    if request.document_ids:
        try:
            for doc_id in request.document_ids:
                document_service.require_document(db, doc_id, owner_id)
        except DocumentNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        answer, sources = llamaindex_service.query(
            request.question,
            owner_id=owner_id,
            document_ids=request.document_ids,
            top_k=request.top_k,
        )
    except LlamaIndexNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Chat query failed")
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}") from exc

    return ChatResponse(answer=answer, sources=sources)
