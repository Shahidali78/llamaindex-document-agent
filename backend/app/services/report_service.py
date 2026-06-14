"""Report generation combining summaries and structured extraction."""

from __future__ import annotations

from datetime import datetime, timezone

from app.db.models import Document
from app.schemas.extraction_schema import ExtractionResult


def _bullets(items: list[str]) -> str:
    if not items:
        return "_None identified._"
    return "\n".join(f"- {item}" for item in items)


def build_report(
    document: Document,
    extraction: ExtractionResult | None,
    summary: str | None,
) -> str:
    """Build a human-readable markdown intelligence report for a document."""
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    title = (extraction.title if extraction and extraction.title else document.filename) or document.filename

    lines: list[str] = [
        f"# Document Intelligence Report: {title}",
        "",
        f"- **Source file:** {document.filename}",
        f"- **Document id:** {document.id}",
        f"- **File type:** {document.file_type}",
        f"- **Indexed chunks:** {document.num_chunks}",
        f"- **Generated:** {generated}",
        "",
    ]

    if extraction is not None:
        lines += [
            "## Overview",
            "",
            f"- **Detected type:** {extraction.document_type or 'unknown'}",
            "",
            "## Key People & Organizations",
            "",
            _bullets(extraction.key_people),
            "",
            "## Key Dates",
            "",
            _bullets(extraction.key_dates),
            "",
            "## Prices & Amounts",
            "",
            _bullets(extraction.prices_or_amounts),
            "",
            "## Obligations",
            "",
            _bullets(extraction.obligations),
            "",
            "## Risks",
            "",
            _bullets(extraction.risks),
            "",
            "## Action Items",
            "",
            _bullets(extraction.action_items),
            "",
        ]

    summary_text = summary or (extraction.summary if extraction else "") or "_No summary available._"
    lines += ["## Summary", "", summary_text, ""]

    return "\n".join(lines).strip() + "\n"
