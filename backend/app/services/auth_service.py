"""API key management: generation, hashing, verification, and CRUD."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import ApiKey
from app.utils.logger import get_logger

logger = get_logger(__name__)

KEY_PREFIX = "dia_"  # "document intelligence api"


def _hash_key(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()


def generate_key() -> tuple[str, str]:
    """Return ``(plaintext, prefix)`` for a freshly generated key."""
    plaintext = f"{KEY_PREFIX}{secrets.token_urlsafe(32)}"
    prefix = plaintext[:12]
    return plaintext, prefix


def create_api_key(db: Session, name: str) -> tuple[ApiKey, str]:
    """Create and persist a new API key. Returns ``(record, plaintext)``."""
    plaintext, prefix = generate_key()
    record = ApiKey(
        name=name,
        prefix=prefix,
        key_hash=_hash_key(plaintext),
        active=True,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("Created API key '%s' (%s…)", name, prefix)
    return record, plaintext


def list_api_keys(db: Session) -> list[ApiKey]:
    return db.query(ApiKey).order_by(ApiKey.created_at.desc()).all()


def revoke_api_key(db: Session, key_id: str) -> bool:
    record = db.get(ApiKey, key_id)
    if record is None:
        return False
    record.active = False
    db.add(record)
    db.commit()
    logger.info("Revoked API key %s", key_id)
    return True


def verify_api_key(db: Session, plaintext: str) -> ApiKey | None:
    """Return the active ApiKey matching the plaintext, updating last_used_at."""
    record = (
        db.query(ApiKey)
        .filter(ApiKey.key_hash == _hash_key(plaintext), ApiKey.active.is_(True))
        .first()
    )
    if record is None:
        return None
    record.last_used_at = datetime.now(timezone.utc)
    db.add(record)
    db.commit()
    return record
