"""Integration tests for edit (modify) flow with FeedbackSignal (T043)."""
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
        description_text="Original description",
        suggested_price=100.0,
        confidence_score=0.8,
        rationale_internal={},
        rationale_external={},
        status="in_review",
    )
    db.add(proposal)
    db.commit()
    pid = str(proposal.id)
    db.close()
    return pid


def test_edit_description_creates_feedback_signal(client):
    from backend.src.config.database import engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select
    from backend.src.models.ai_proposal import AIProposal
    from backend.src.models.feedback_signal import FeedbackSignal

    session_id = "edit-session-1"
    pid = _create_proposal(engine)

    # Acquire lock
    client.post(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": session_id})

    # Edit description
    res = client.post(
        f"/api/v1/proposals/{pid}/review",
        json={"decision": "edit", "edited_description": "New description"},
        headers={"X-Session-Id": session_id},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["next_status"] == "modified_pending_reapproval"
    assert data["feedback_signals_created"] == 1

    # Verify DB
    Session = sessionmaker(bind=engine)
    db = Session()
    proposal = db.scalar(select(AIProposal).where(AIProposal.id == uuid.UUID(pid)))
    assert proposal.status == "modified_pending_reapproval"
    signals = list(db.scalars(select(FeedbackSignal).where(FeedbackSignal.proposal_id == uuid.UUID(pid))).all())
    assert len(signals) == 1
    assert signals[0].field_name == "description_text"
    assert signals[0].original_value == "Original description"
    assert signals[0].corrected_value == "New description"
    db.close()


def test_edit_no_changes_returns_422(client):
    from backend.src.config.database import engine
    session_id = "edit-session-nochange"
    pid = _create_proposal(engine)
    client.post(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": session_id})
    res = client.post(
        f"/api/v1/proposals/{pid}/review",
        json={"decision": "edit", "edited_description": "Original description"},
        headers={"X-Session-Id": session_id},
    )
    assert res.status_code == 422


def test_modified_proposal_appears_first_in_queue(client):
    from backend.src.config.database import engine
    from sqlalchemy.orm import sessionmaker
    from backend.src.models.product import Product
    from backend.src.models.ai_proposal import AIProposal
    from sqlalchemy import select

    Session = sessionmaker(bind=engine)
    db = Session()

    # Create two proposals: one normal, one modified
    p1 = Product(id=uuid.uuid4(), source_channel="api", status="in_review", tags={})
    db.add(p1)
    db.flush()
    normal = AIProposal(
        id=uuid.uuid4(),
        product_id=p1.id,
        description_text="Normal",
        suggested_price=10,
        confidence_score=0.7,
        rationale_internal={},
        rationale_external={},
        status="in_review",
    )
    db.add(normal)

    p2 = Product(id=uuid.uuid4(), source_channel="api", status="in_review", tags={})
    db.add(p2)
    db.flush()
    modified = AIProposal(
        id=uuid.uuid4(),
        product_id=p2.id,
        description_text="Modified",
        suggested_price=20,
        confidence_score=0.8,
        rationale_internal={},
        rationale_external={},
        status="modified_pending_reapproval",
    )
    db.add(modified)
    db.commit()
    modified_id = str(modified.id)
    modified_uuid = modified.id
    normal_uuid = normal.id
    db.close()

    # Retire other in_review proposals from the queue by marking them approved
    # so only our two proposals are active
    from sqlalchemy import update
    db2 = Session()
    db2.execute(
        update(AIProposal)
        .where(
            AIProposal.status.in_(["in_review", "modified_pending_reapproval"]),
            AIProposal.id != normal_uuid,
            AIProposal.id != modified_uuid,
        )
        .values(status="approved")
    )
    db2.commit()
    db2.close()

    res = client.get("/api/v1/review-queue", headers={"X-Session-Id": "priority-session"})
    assert res.status_code == 200
    data = res.json()
    assert data["proposal_id"] == modified_id
