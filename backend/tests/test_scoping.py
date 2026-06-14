"""Tests for per-key document ownership scoping."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.services.llamaindex_service import llamaindex_service


@pytest.fixture
def two_keys(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> tuple[str, str]:
    """Enable auth, stub indexing, and mint two distinct managed keys."""
    monkeypatch.setattr(settings, "auth_enabled", True)
    monkeypatch.setattr(settings, "api_keys", "")
    monkeypatch.setattr(settings, "admin_api_token", "admin-secret")
    monkeypatch.setattr(llamaindex_service, "add_document", lambda *a, **k: 2)

    admin = {"X-Admin-Token": "admin-secret"}
    key_a = client.post("/auth/keys", json={"name": "tenant-a"}, headers=admin).json()["api_key"]
    key_b = client.post("/auth/keys", json={"name": "tenant-b"}, headers=admin).json()["api_key"]
    return key_a, key_b


def _upload(client: TestClient, key: str, name: str) -> str:
    files = {"file": (name, b"Tenant private content.", "text/plain")}
    res = client.post("/documents/upload", files=files, headers={"X-API-Key": key})
    assert res.status_code == 200
    return res.json()["document"]["id"]


def test_documents_are_isolated_per_key(
    client: TestClient, two_keys: tuple[str, str]
) -> None:
    key_a, key_b = two_keys
    doc_id = _upload(client, key_a, "a.txt")

    # Owner A sees their document.
    list_a = client.get("/documents", headers={"X-API-Key": key_a}).json()
    assert list_a["count"] == 1
    assert list_a["documents"][0]["id"] == doc_id

    # Owner B sees nothing.
    list_b = client.get("/documents", headers={"X-API-Key": key_b}).json()
    assert list_b["count"] == 0


def test_cannot_fetch_another_keys_document(
    client: TestClient, two_keys: tuple[str, str]
) -> None:
    key_a, key_b = two_keys
    doc_id = _upload(client, key_a, "a.txt")

    assert client.get(f"/documents/{doc_id}", headers={"X-API-Key": key_a}).status_code == 200
    assert client.get(f"/documents/{doc_id}", headers={"X-API-Key": key_b}).status_code == 404


def test_cannot_operate_on_another_keys_document(
    client: TestClient, two_keys: tuple[str, str]
) -> None:
    key_a, key_b = two_keys
    doc_id = _upload(client, key_a, "a.txt")

    # B cannot extract / summarize / report on A's document.
    assert client.post("/extract", json={"document_id": doc_id}, headers={"X-API-Key": key_b}).status_code == 404
    assert client.post("/summarize", json={"document_id": doc_id}, headers={"X-API-Key": key_b}).status_code == 404
    assert client.post("/generate-report", json={"document_id": doc_id}, headers={"X-API-Key": key_b}).status_code == 404

    # B cannot scope a chat to A's document.
    res = client.post(
        "/chat",
        json={"question": "what is this?", "document_ids": [doc_id]},
        headers={"X-API-Key": key_b},
    )
    assert res.status_code == 404
