"""Tests for chat, extract, summarize, compare, and report endpoints.

All LLM/index calls are monkeypatched so the suite runs offline.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.schemas.chat_schema import SourceNode
from app.schemas.extraction_schema import ExtractionResult
from app.services import extraction_service
from app.services.llamaindex_service import llamaindex_service


@pytest.fixture(autouse=True)
def stub_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llamaindex_service, "add_document", lambda *a, **k: 2)
    monkeypatch.setattr(
        llamaindex_service,
        "query",
        lambda *a, **k: (
            "This is a test answer.",
            [SourceNode(document_id="d1", filename="sample.txt", snippet="snippet", score=0.9)],
        ),
    )
    monkeypatch.setattr(
        extraction_service,
        "extract_fields",
        lambda text, filename: ExtractionResult(
            document_type="contract", title="Test", summary="A test summary."
        ),
    )
    monkeypatch.setattr(extraction_service, "summarize", lambda *a, **k: "A test summary.")
    monkeypatch.setattr(extraction_service, "compare", lambda *a, **k: "Comparison result.")


def _upload(client: TestClient, name: str = "sample.txt") -> str:
    files = {"file": (name, b"Hello contract world. Party A pays Party B $100.", "text/plain")}
    return client.post("/documents/upload", files=files).json()["document"]["id"]


def test_chat(client: TestClient) -> None:
    response = client.post("/chat", json={"question": "What is this about?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "This is a test answer."
    assert body["sources"][0]["filename"] == "sample.txt"


def test_chat_validation(client: TestClient) -> None:
    response = client.post("/chat", json={"question": ""})
    assert response.status_code == 422


def test_extract(client: TestClient) -> None:
    doc_id = _upload(client)
    response = client.post("/extract", json={"document_id": doc_id})
    assert response.status_code == 200
    assert response.json()["extraction"]["document_type"] == "contract"


def test_summarize(client: TestClient) -> None:
    doc_id = _upload(client)
    response = client.post("/summarize", json={"document_id": doc_id})
    assert response.status_code == 200
    assert response.json()["summary"] == "A test summary."


def test_compare(client: TestClient) -> None:
    doc_a = _upload(client, "a.txt")
    doc_b = _upload(client, "b.txt")
    response = client.post(
        "/compare", json={"document_id_a": doc_a, "document_id_b": doc_b}
    )
    assert response.status_code == 200
    assert response.json()["comparison"] == "Comparison result."


def test_compare_same_document_rejected(client: TestClient) -> None:
    doc_id = _upload(client)
    response = client.post(
        "/compare", json={"document_id_a": doc_id, "document_id_b": doc_id}
    )
    assert response.status_code == 400


def test_generate_report(client: TestClient) -> None:
    doc_id = _upload(client)
    response = client.post("/generate-report", json={"document_id": doc_id})
    assert response.status_code == 200
    body = response.json()
    assert "# Document Intelligence Report" in body["report_markdown"]
    assert body["extraction"]["document_type"] == "contract"


def test_extract_missing_document(client: TestClient) -> None:
    response = client.post("/extract", json={"document_id": "nope"})
    assert response.status_code == 404
