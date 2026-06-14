"""Authentication dependencies for protecting endpoints.

Two layers:
- ``require_api_key``  — guards data/AI endpoints via the ``X-API-Key`` header.
  Accepts either a static key (from ``API_KEYS``) or an active DB-backed key.
- ``require_admin``    — guards the /auth key-management API via ``X-Admin-Token``.
"""

from __future__ import annotations

import hashlib
import hmac

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.services import auth_service, usage_service


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> str:
    """Validate the request's API key and return a stable owner identifier.

    The returned value is used to scope document ownership:
    - auth disabled        -> "public" (single shared space)
    - static key (API_KEYS) -> "static:<sha256-prefix>" (per-key isolation)
    - managed DB key        -> the key's id
    """
    if not settings.auth_enabled:
        return "public"

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide it in the 'X-API-Key' header.",
        )

    # 1) Static keys configured via the API_KEYS env var.
    for key in settings.api_key_list:
        if hmac.compare_digest(x_api_key, key):
            digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
            return f"static:{digest}"

    # 2) DB-backed keys (hashed).
    record = auth_service.verify_api_key(db, x_api_key)
    if record is not None:
        return record.id

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or revoked API key.",
    )


# Maps (method, path) of a tracked operation to its usage counter.
_ACTION_BY_ROUTE = {
    ("POST", "/documents/upload"): "uploads",
    ("POST", "/chat"): "chats",
    ("POST", "/extract"): "extractions",
    ("POST", "/summarize"): "summaries",
    ("POST", "/compare"): "comparisons",
    ("POST", "/generate-report"): "reports",
}


def track_usage(
    request: Request,
    owner_id: str = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> None:
    """Record one request against the caller's usage counters.

    Counts received requests (runs before the handler), bumping the total and,
    for known operations, the matching action counter.
    """
    action = _ACTION_BY_ROUTE.get((request.method, request.url.path))
    try:
        usage_service.record(db, owner_id, action)
    except Exception:  # noqa: BLE001 - usage tracking must never break a request
        db.rollback()


def require_admin(
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> bool:
    """Guard the key-management API with the admin token."""
    if not settings.admin_api_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Key management is disabled. Set ADMIN_API_TOKEN to enable it.",
        )
    if not x_admin_token or not hmac.compare_digest(x_admin_token, settings.admin_api_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token.",
        )
    return True
