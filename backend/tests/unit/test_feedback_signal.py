"""Unit tests for FeedbackSignal creation logic (T042)."""
import uuid
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from backend.src.models.base import Base
from backend.src.models import (  # noqa: F401
    ai_proposal, product, operator_review, feedback_signal as fs_model,
    review_lock as rl_model
)
from backend.src.services.review_service import ReviewService


@pytest.fixture(scope="module")
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


def _setup_proposal(db, desc="Original", price=100.0):
    from backend.src.models.product import Product
    from backend.src.models.ai_proposal import AIProposal
    p = Product(id=uuid.uuid4(), source_channel="api", status="in_review", tags={})
    db.add(p)
    db.flush()
    proposal = AIProposal(
        id=uuid.uuid4(),
        product_id=p.id,
        description_text=desc,
        suggested_price=price,
        confidence_score=0.8,
        rationale_internal={},
        rationale_external={},
        status="in_review",
    )
    db.add(proposal)
    db.commit()
    return str(proposal.id)


def test_create_one_feedback_signal_for_description(db):
    from backend.src.models.feedback_signal import FeedbackSignal
    pid = _setup_proposal(db, desc="Original desc", price=100.0)
    svc = ReviewService(db)
    _, signals = svc.review(pid, {
        "decision": "edit",
        "edited_description": "New desc",
    })
    assert len(signals) == 1
    assert signals[0].field_name == "description_text"
    assert signals[0].original_value == "Original desc"
    assert signals[0].corrected_value == "New desc"


def test_create_two_feedback_signals(db):
    pid = _setup_proposal(db, desc="Desc", price=50.0)
    svc = ReviewService(db)
    _, signals = svc.review(pid, {
        "decision": "edit",
        "edited_description": "Different desc",
        "edited_price": 75.0,
    })
    assert len(signals) == 2
    fields = {s.field_name for s in signals}
    assert fields == {"description_text", "suggested_price"}


def test_edit_no_actual_changes_raises(db):
    pid = _setup_proposal(db, desc="Same", price=100.0)
    svc = ReviewService(db)
    with pytest.raises(ValueError, match="edit_no_changes"):
        svc.review(pid, {
            "decision": "edit",
            "edited_description": "Same",
            "edited_price": 100.0,
        })
