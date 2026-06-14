"""SQLAlchemy ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.db.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    """Metadata for an uploaded and indexed document."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=_uuid)
    owner_id = Column(String, nullable=False, index=True, default="public")
    filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # ".pdf", ".txt", ".docx"
    size_bytes = Column(Integer, default=0, nullable=False)
    num_chunks = Column(Integer, default=0, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending|indexed|failed
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "filename": self.filename,
            "file_type": self.file_type,
            "size_bytes": self.size_bytes,
            "num_chunks": self.num_chunks,
            "status": self.status,
            "error": self.error,
            "created_at": self.created_at,
        }


class ApiKey(Base):
    """A hashed API key used to authenticate requests.

    The plaintext key is shown only once at creation; only its SHA-256 hash is
    stored. ``prefix`` is a non-secret label (start of the key) for identification.
    """

    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    prefix = Column(String, nullable=False)
    key_hash = Column(String, nullable=False, unique=True, index=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)


class UsageStat(Base):
    """Aggregated per-owner usage counters.

    ``owner_id`` matches the identifier returned by the auth layer (a managed
    key id, ``static:<hash>``, or ``public``), so usage is tracked for every
    kind of caller — not only managed keys.
    """

    __tablename__ = "usage_stats"

    owner_id = Column(String, primary_key=True)
    total_requests = Column(Integer, default=0, nullable=False)
    uploads = Column(Integer, default=0, nullable=False)
    chats = Column(Integer, default=0, nullable=False)
    extractions = Column(Integer, default=0, nullable=False)
    summaries = Column(Integer, default=0, nullable=False)
    comparisons = Column(Integer, default=0, nullable=False)
    reports = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    last_request_at = Column(DateTime, nullable=True)
