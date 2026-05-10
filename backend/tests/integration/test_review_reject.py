"""Integration tests for reject flow (T044)."""
import uuid


def _create_proposal(engine):
    from sqlalchemy.orm import sessionmaker
    from backend.src.models.product import Product
    from backend.src.models.ai_proposal import AIProposal
    Session = sessionmaker(bind=engine)
    db = Session()
    p = Product(id=uuid.uuid4(), source_channel="api", status="in_review", tags={})
    db.add(p)
    db.flush()
    proposal = AIProposal(
        id=uuid.uuid4(),
        product_id=p.id,
        description_text="Reject test",
        suggested_price=50.0,
        confidence_score=0.7,
        rationale_internal={},
        rationale_external={},
        status="in_review",
    )
    db.add(proposal)
    db.commit()
    pid = str(proposal.id)
    db.close()
    return pid


def test_reject_without_edit_no_feedback_signal(client):
    from backend.src.config.database import engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select
    from backend.src.models.ai_proposal import AIProposal
    from backend.src.models.operator_review import OperatorReview
    from backend.src.models.feedback_signal import FeedbackSignal
    from backend.src.models.review_lock import ReviewLock

    session_id = "reject-session-1"
    pid = _create_proposal(engine)

    client.post(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": session_id})

    res = client.post(
        f"/api/v1/proposals/{pid}/review",
        json={"decision": "reject", "reject_reason": "Precio incorrecto"},
        headers={"X-Session-Id": session_id},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "reject"
    assert data["next_status"] == "rejected"
    assert data["feedback_signals_created"] == 0

    # Verify no FeedbackSignal, lock released
    Session = sessionmaker(bind=engine)
    db = Session()
    signals = list(db.scalars(select(FeedbackSignal).where(FeedbackSignal.proposal_id == uuid.UUID(pid))).all())
    assert len(signals) == 0
    lock = db.scalar(select(ReviewLock).where(ReviewLock.proposal_id == uuid.UUID(pid)))
    assert lock is None
    db.close()
