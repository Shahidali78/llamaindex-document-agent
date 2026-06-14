"""Tests for per-key usage tracking."""

from __future__ import annotations

import hashlib
import uuid

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.services.llamaindex_service import llamaindex_service


@pytest.fixture
def usage_key(monkeypatch: pytest.MonkeyPatch) -> tuple[str, str, dict[str, str]]:
    """Enable auth with a unique static key per test (isolated usage counters)."""
    key = f"usage-test-{uuid.uuid4().hex}"
    owner_id = "static:" + hashlib.sha256(key.encode()).hexdigest()[:16]
    monkeypatch.setattr(settings, "auth_enabled", True)
    monkeypatch.setattr(settings, "api_keys", key)
    monkeypatch.setattr(settings, "admin_api_token", "admin-secret")
    monkeypatch.setattr(llamaindex_service, "add_document", lambda *a, **k: 1)
    monkeypatch.setattr(llamaindex_service, "query", lambda *a, **k: ("answer", []))
    return key, owner_id, {"X-API-Key": key}


def _make_some_requests(client: TestClient, auth: dict[str, str]) -> None:
    files = {"file": ("u.txt", b"hello", "text/plain")}
    assert client.post("/documents/upload", files=files, headers=auth).status_code == 200
    assert client.post("/chat", json={"question": "hi"}, headers=auth).status_code == 200
    assert client.get("/documents", headers=auth).status_code == 200


def test_self_usage_counts(client: TestClient, usage_key) -> None:
    _key, owner_id, auth = usage_key
    _make_some_requests(client, auth)

    res = client.get("/usage", headers=auth)
    assert res.status_code == 200
    body = res.json()
    assert body["owner_id"] == owner_id
    assert body["uploads"] == 1
    assert body["chats"] == 1
    assert body["document_count"] == 1
    # upload + chat + list + this /usage call all count toward the total.
    assert body["total_requests"] == 4
    assert body["last_request_at"] is not None


def test_usage_requires_key(client: TestClient, usage_key) -> None:
    assert client.get("/usage").status_code == 401


def test_admin_usage_overview(client: TestClient, usage_key) -> None:
    _key, owner_id, auth = usage_key
    _make_some_requests(client, auth)

    res = client.get("/auth/usage", headers={"X-Admin-Token": "admin-secret"})
    assert res.status_code == 200
    body = res.json()
    owner_row = next((u for u in body["usage"] if u["owner_id"] == owner_id), None)
    assert owner_row is not None
    assert owner_row["uploads"] == 1
    assert owner_row["chats"] == 1


def test_admin_usage_requires_admin_token(client: TestClient, usage_key) -> None:
    assert client.get("/auth/usage").status_code == 401
