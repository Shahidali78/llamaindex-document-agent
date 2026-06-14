"""Tests for API key authentication and the admin key-management API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import settings


@pytest.fixture
def auth_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """Enable auth with a single static key for the duration of a test."""
    monkeypatch.setattr(settings, "auth_enabled", True)
    monkeypatch.setattr(settings, "api_keys", "secret-static-key")


def test_protected_route_requires_key(client: TestClient, auth_on: None) -> None:
    res = client.get("/documents")
    assert res.status_code == 401
    assert "API key" in res.json()["detail"]


def test_protected_route_rejects_bad_key(client: TestClient, auth_on: None) -> None:
    res = client.get("/documents", headers={"X-API-Key": "wrong"})
    assert res.status_code == 401


def test_protected_route_accepts_static_key(client: TestClient, auth_on: None) -> None:
    res = client.get("/documents", headers={"X-API-Key": "secret-static-key"})
    assert res.status_code == 200


def test_health_is_public_when_auth_on(client: TestClient, auth_on: None) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["auth_enabled"] is True


def test_admin_disabled_without_token(client: TestClient, auth_on: None) -> None:
    # admin_api_token is unset -> management API is disabled.
    res = client.post("/auth/keys", json={"name": "ci"})
    assert res.status_code == 403


def test_admin_mint_and_use_key(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "auth_enabled", True)
    monkeypatch.setattr(settings, "api_keys", "")
    monkeypatch.setattr(settings, "admin_api_token", "admin-secret")
    admin = {"X-Admin-Token": "admin-secret"}

    # Wrong admin token rejected.
    assert client.post("/auth/keys", json={"name": "x"}, headers={"X-Admin-Token": "nope"}).status_code == 401

    # Mint a key.
    created = client.post("/auth/keys", json={"name": "demo"}, headers=admin)
    assert created.status_code == 201
    body = created.json()
    plaintext = body["api_key"]
    assert plaintext.startswith("dia_")
    assert body["prefix"] == plaintext[:12]

    # The minted key works on a protected route.
    assert client.get("/documents", headers={"X-API-Key": plaintext}).status_code == 200

    # It appears in the list (without the secret).
    listed = client.get("/auth/keys", headers=admin).json()
    assert any(k["id"] == body["id"] for k in listed)
    assert all("api_key" not in k for k in listed)

    # Revoke it -> the key stops working.
    assert client.delete(f"/auth/keys/{body['id']}", headers=admin).status_code == 200
    assert client.get("/documents", headers={"X-API-Key": plaintext}).status_code == 401
