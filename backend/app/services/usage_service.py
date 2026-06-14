"""Per-owner usage tracking."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import Document, UsageStat
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Maps a tracked action to its counter column on UsageStat.
ACTION_COLUMNS = {
    "uploads",
    "chats",
    "extractions",
    "summaries",
    "comparisons",
    "reports",
}


def get_or_create(db: Session, owner_id: str) -> UsageStat:
    stat = db.get(UsageStat, owner_id)
    if stat is None:
        stat = UsageStat(owner_id=owner_id)
        db.add(stat)
        db.commit()
        db.refresh(stat)
    return stat


def record(db: Session, owner_id: str, action: str | None = None) -> None:
    """Increment total request count (and an action counter, if given)."""
    stat = get_or_create(db, owner_id)
    stat.total_requests += 1
    if action in ACTION_COLUMNS:
        setattr(stat, action, getattr(stat, action) + 1)
    stat.last_request_at = datetime.now(timezone.utc)
    db.add(stat)
    db.commit()


def get(db: Session, owner_id: str) -> UsageStat | None:
    return db.get(UsageStat, owner_id)


def list_all(db: Session) -> list[UsageStat]:
    return db.query(UsageStat).order_by(UsageStat.total_requests.desc()).all()


def document_count(db: Session, owner_id: str) -> int:
    return db.query(Document).filter(Document.owner_id == owner_id).count()


def serialize(db: Session, stat: UsageStat, name: str | None = None) -> dict:
    """Build a UsageResponse-shaped dict, including the live document count."""
    return {
        "owner_id": stat.owner_id,
        "name": name,
        "total_requests": stat.total_requests,
        "uploads": stat.uploads,
        "chats": stat.chats,
        "extractions": stat.extractions,
        "summaries": stat.summaries,
        "comparisons": stat.comparisons,
        "reports": stat.reports,
        "document_count": document_count(db, stat.owner_id),
        "created_at": stat.created_at,
        "last_request_at": stat.last_request_at,
    }
