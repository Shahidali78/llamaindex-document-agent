"""Pydantic schemas for structured extraction, summarization, and comparison."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExtractionResult(BaseModel):
    """Structured fields extracted from a document.

    Also used directly as the LlamaIndex structured-prediction output schema, so
    every field carries a description to guide the LLM.
    """

    document_type: str = Field(
        default="", description="The type of document, e.g. contract, invoice, report, resume"
    )
    title: str = Field(default="", description="The document title or a concise descriptive title")
    key_people: list[str] = Field(
        default_factory=list, description="Names of people or organizations mentioned"
    )
    key_dates: list[str] = Field(
        default_factory=list, description="Important dates found in the document"
    )
    prices_or_amounts: list[str] = Field(
        default_factory=list, description="Monetary amounts, prices, or financial figures"
    )
    obligations: list[str] = Field(
        default_factory=list, description="Duties, commitments, or obligations stated"
    )
    risks: list[str] = Field(
        default_factory=list, description="Risks, liabilities, or potential issues"
    )
    action_items: list[str] = Field(
        default_factory=list, description="Concrete next steps or required actions"
    )
    summary: str = Field(default="", description="A concise summary of the document")


# --- Request / response wrappers ---


class ExtractRequest(BaseModel):
    document_id: str


class ExtractResponse(BaseModel):
    document_id: str
    filename: str
    extraction: ExtractionResult


class SummarizeRequest(BaseModel):
    document_id: str
    style: str = Field(
        default="concise",
        description="Summary style hint, e.g. 'concise', 'detailed', 'bullet points'",
    )


class SummarizeResponse(BaseModel):
    document_id: str
    filename: str
    summary: str


class CompareRequest(BaseModel):
    document_id_a: str
    document_id_b: str
    focus: str = Field(
        default="",
        description="Optional aspect to focus the comparison on, e.g. 'pricing', 'obligations'",
    )


class CompareResponse(BaseModel):
    document_id_a: str
    document_id_b: str
    filename_a: str
    filename_b: str
    comparison: str
