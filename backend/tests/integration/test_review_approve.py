"""Integration tests for approve flow (T034)."""
import uuid


def _create_proposal_with_lock(engine, session_id):
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
        description_text="Approve test",
        suggested_price=75.0,
        confidence_score=0.9,
        rationale_internal={},
        rationale_external={},
        status="in_review",
    )
    db.add(proposal)
    db.commit()
    pid = str(proposal.id)
    product_id = str(p.id)
    db.close()
    return pid, product_id


def test_approve_flow(client):
    from backend.src.config.database import engine
    from sqlalchemy.orm import sessionmaker
    from backend.src.models.ai_proposal import AIProposal
    from backend.src.models.product import Product
    from backend.src.models.review_lock import ReviewLock
    from sqlalchemy import select

    session_id = "approve-session"
    pid, product_id = _create_proposal_with_lock(engine, session_id)

    # Acquire lock
    lock_res = client.post(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": session_id})
    assert lock_res.status_code == 200

    # Approve
    review_res = client.post(
        f"/api/v1/proposals/{pid}/review",
        json={"decision": "approve"},
        headers={"X-Session-Id": session_id},
    )
    assert review_res.status_code == 200
    data = review_res.json()
    assert data["decision"] == "approve"
    assert data["next_status"] == "approved"

    # Verify DB state
    Session = sessionmaker(bind=engine)
    db = Session()
    proposal = db.scalar(select(AIProposal).where(AIProposal.id == uuid.UUID(pid)))
    assert proposal.status == "approved"
    product = db.scalar(select(Product).where(Product.id == proposal.product_id))
    assert product.status == "approved"
    lock = db.scalar(select(ReviewLock).where(ReviewLock.proposal_id == uuid.UUID(pid)))
    assert lock is None  # Released after approve
    db.close()
