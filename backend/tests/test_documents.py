"""Document upload and retrieval tests (indexing is monkeypatched)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.services.llamaindex_service import llamaindex_service


@pytest.fixture(autouse=True)
def stub_indexing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid real OpenAI/Chroma calls during upload tests."""
    monkeypatch.setattr(llamaindex_service, "add_document", lambda *a, **k: 3)


def _upload(client: TestClient, name: str = "sample.txt", content: bytes = b"Hello contract world.") -> dict:
    files = {"file": (name, content, "text/plain")}
    response = client.post("/documents/upload", files=files)
    return response


def test_upload_txt(client: TestClient) -> None:
    response = _upload(client)
    assert response.status_code == 200
    body = response.json()
    assert body["document"]["status"] == "indexed"
    assert body["document"]["num_chunks"] == 3
    assert body["document"]["file_type"] == ".txt"


def test_upload_unsupported_type(client: TestClient) -> None:
    files = {"file": ("malware.exe", b"MZ", "application/octet-stream")}
    response = client.post("/documents/upload", files=files)
    assert response.status_code == 400


def test_list_and_get_document(client: TestClient) -> None:
    upload = _upload(client, name="second.txt").json()
    doc_id = upload["document"]["id"]

    listing = client.get("/documents")
    assert listing.status_code == 200
    assert listing.json()["count"] >= 1

    single = client.get(f"/documents/{doc_id}")
    assert single.status_code == 200
    assert single.json()["id"] == doc_id


def test_get_missing_document(client: TestClient) -> None:
    response = client.get("/documents/does-not-exist")
    assert response.status_code == 404
