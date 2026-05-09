"""Unit tests for ReviewLockService (T014)."""
import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.src.models.base import Base
from backend.src.models import ai_proposal, product, review_lock as rl_model  # noqa: F401
from backend.src.services.review_lock_service import ReviewLockService, LOCK_TTL_SECONDS


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


def _add_proposal(db) -> uuid.UUID:
    from backend.src.models.product import Product
    from backend.src.models.ai_proposal import AIProposal
    pid = uuid.uuid4()
    p = Product(id=uuid.uuid4(), source_channel="api", status="in_review", tags={})
    db.add(p)
    db.flush()
    proposal = AIProposal(
        id=pid,
        product_id=p.id,
        description_text="test",
        suggested_price=10,
        confidence_score=0.9,
        rationale_internal={},
        rationale_external={},
    )
    db.add(proposal)
    db.commit()
    return pid


def test_acquire_creates_lock(db):
    proposal_id = _add_proposal(db)
    svc = ReviewLockService(db)
    lock = svc.acquire(proposal_id, "session-1")
    assert lock.proposal_id == proposal_id
    assert lock.session_id == "session-1"
    assert lock.expires_at > datetime.utcnow()


def test_acquire_renews_same_session(db):
    proposal_id = _add_proposal(db)
    svc = ReviewLockService(db)
    lock1 = svc.acquire(proposal_id, "session-1")
    lock2 = svc.acquire(proposal_id, "session-1")
    assert lock1.id == lock2.id
    assert lock2.expires_at >= lock1.expires_at


def test_acquire_conflict_different_session(db):
    proposal_id = _add_proposal(db)
    svc = ReviewLockService(db)
    svc.acquire(proposal_id, "session-1")
    with pytest.raises(ValueError, match="lock_conflict"):
        svc.acquire(proposal_id, "session-OTHER")


def test_renew_ttl(db):
    proposal_id = _add_proposal(db)
    svc = ReviewLockService(db)
    svc.acquire(proposal_id, "session-1")
    lock = svc.renew(proposal_id, "session-1")
    assert lock.expires_at > datetime.utcnow()


def test_renew_wrong_session(db):
    proposal_id = _add_proposal(db)
    svc = ReviewLockService(db)
    svc.acquire(proposal_id, "session-1")
    with pytest.raises(ValueError):
        svc.renew(proposal_id, "session-WRONG")


def test_release_removes_lock(db):
    proposal_id = _add_proposal(db)
    svc = ReviewLockService(db)
    svc.acquire(proposal_id, "session-1")
    svc.release(proposal_id, "session-1")
    # After release, new session can acquire
    lock = svc.acquire(proposal_id, "session-2")
    assert lock.session_id == "session-2"


def test_release_forbidden_other_session(db):
    proposal_id = _add_proposal(db)
    svc = ReviewLockService(db)
    svc.acquire(proposal_id, "session-A")
    with pytest.raises(ValueError, match="lock_forbidden"):
        svc.release(proposal_id, "session-B")


def test_expired_lock_cleaned_on_acquire(db):
    proposal_id = _add_proposal(db)
    svc = ReviewLockService(db)
    lock = svc.acquire(proposal_id, "session-exp")
    # Manually expire
    lock.expires_at = datetime.utcnow() - timedelta(seconds=1)
    db.commit()
    # Now another session can acquire
    new_lock = svc.acquire(proposal_id, "session-new")
    assert new_lock.session_id == "session-new"

