import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.models.review_lock import ReviewLock

LOCK_TTL_SECONDS = 60


class ReviewLockService:
    def __init__(self, db: Session):
        self.db = db

    def _clean_expired(self) -> None:
        """Remove locks whose TTL has expired."""
        now = datetime.utcnow()
        expired = self.db.scalars(
            select(ReviewLock).where(ReviewLock.expires_at <= now)
        ).all()
        for lock in expired:
            self.db.delete(lock)
        if expired:
            self.db.flush()

    def _get_lock(self, proposal_id: uuid.UUID) -> ReviewLock | None:
        return self.db.scalar(
            select(ReviewLock).where(ReviewLock.proposal_id == proposal_id)
        )

    def acquire(self, proposal_id: uuid.UUID, session_id: str) -> ReviewLock:
        """Acquire or renew a lock. Raises ValueError if held by another session."""
        self._clean_expired()
        existing = self._get_lock(proposal_id)
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=LOCK_TTL_SECONDS)

        if existing is not None:
            if existing.session_id != session_id:
                raise ValueError("lock_conflict")
            existing.locked_at = now
            existing.expires_at = expires_at
            self.db.flush()
            return existing

        lock = ReviewLock(
            proposal_id=proposal_id,
            session_id=session_id,
            locked_at=now,
            expires_at=expires_at,
        )
        self.db.add(lock)
        self.db.commit()
        self.db.refresh(lock)
        return lock

    def renew(self, proposal_id: uuid.UUID, session_id: str) -> ReviewLock:
        """Renew TTL of an existing lock. Raises ValueError if not found or wrong session."""
        self._clean_expired()
        lock = self._get_lock(proposal_id)
        if lock is None:
            raise ValueError("lock_not_found")
        if lock.session_id != session_id:
            raise ValueError("lock_conflict")
        now = datetime.utcnow()
        lock.locked_at = now
        lock.expires_at = now + timedelta(seconds=LOCK_TTL_SECONDS)
        self.db.commit()
        self.db.refresh(lock)
        return lock

    def release(self, proposal_id: uuid.UUID, session_id: str) -> None:
        """Release a lock. Raises ValueError if not owned by this session."""
        lock = self._get_lock(proposal_id)
        if lock is None:
            return  # Already gone (expired or released)
        if lock.session_id != session_id:
            raise ValueError("lock_forbidden")
        self.db.delete(lock)
        self.db.commit()
