"""Pytest fixtures.

The data directory and a dummy API key are configured *before* the app is
imported so that all storage is isolated to a temp directory and tests run
fully offline (the LlamaIndex/OpenAI calls are monkeypatched in each test).
"""

from __future__ import annotations

import os
import tempfile

# Must be set before importing app.config / app.main.
_TMP_DATA_DIR = tempfile.mkdtemp(prefix="llamaidx_test_")
os.environ["DATA_DIR"] = _TMP_DATA_DIR
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used")
# Auth is disabled by default for tests; test_auth.py re-enables it per-test.
os.environ["AUTH_ENABLED"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
