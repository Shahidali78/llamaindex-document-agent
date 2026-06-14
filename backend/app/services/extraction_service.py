"""LLM-powered structured extraction, summarization, and comparison."""

from __future__ import annotations

from app.config import settings
from app.schemas.extraction_schema import ExtractionResult
from app.services.llamaindex_service import llamaindex_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _truncate(text: str) -> str:
    """Limit text sent to the LLM to keep within token budgets."""
    if len(text) <= settings.max_extract_chars:
        return text
    logger.info("Truncating document text from %d to %d chars", len(text), settings.max_extract_chars)
    return text[: settings.max_extract_chars]


def extract_fields(text: str, filename: str) -> ExtractionResult:
    """Extract structured fields from document text using the LLM."""
    from llama_index.core.prompts import PromptTemplate

    if not text.strip():
        return ExtractionResult(document_type="unknown", title=filename)

    llm = llamaindex_service.get_llm()
    prompt = PromptTemplate(
        "You are an expert document analyst. Extract the requested structured "
        "information from the document below. If a field has no relevant content, "
        "return an empty value. Be accurate and do not invent facts.\n\n"
        "Document name: {filename}\n"
        "---------------------\n"
        "{document_text}\n"
        "---------------------\n"
    )
    result = llm.structured_predict(
        ExtractionResult,
        prompt,
        filename=filename,
        document_text=_truncate(text),
    )
    return result


def summarize(text: str, filename: str, style: str = "concise") -> str:
    """Produce a summary of the document text in the requested style."""
    if not text.strip():
        return "The document contains no extractable text to summarize."

    llm = llamaindex_service.get_llm()
    prompt = (
        f"Summarize the following document in a {style} style. "
        f"Capture the main points, key parties, and important details.\n\n"
        f"Document name: {filename}\n"
        "---------------------\n"
        f"{_truncate(text)}\n"
        "---------------------\n"
        "Summary:"
    )
    return str(llm.complete(prompt)).strip()


def compare(
    text_a: str,
    filename_a: str,
    text_b: str,
    filename_b: str,
    focus: str = "",
) -> str:
    """Compare two documents and return a structured markdown comparison."""
    llm = llamaindex_service.get_llm()
    focus_line = f"Focus the comparison on: {focus}.\n" if focus.strip() else ""
    prompt = (
        "Compare the two documents below. Produce a clear markdown comparison that "
        "covers their similarities, their differences, and notable items unique to "
        "each. End with a short overall conclusion.\n"
        f"{focus_line}\n"
        f"=== DOCUMENT A: {filename_a} ===\n"
        f"{_truncate(text_a)}\n\n"
        f"=== DOCUMENT B: {filename_b} ===\n"
        f"{_truncate(text_b)}\n\n"
        "Comparison:"
    )
    return str(llm.complete(prompt)).strip()
