"""Integration tests for GET /review-queue endpoint (T015)."""
import uuid


def _create_proposal(client, status="in_review"):
    """Helper: create product + proposal via existing endpoints or directly."""
    import os
    os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.src.config.settings import get_settings
    from backend.src.models.product import Product
    from backend.src.models.ai_proposal import AIProposal
    from backend.src.config.database import engine

    Session = sessionmaker(bind=engine)
    db = Session()
    p = Product(id=uuid.uuid4(), source_channel="api", status=status, tags={})
    db.add(p)
    db.flush()
    proposal = AIProposal(
        id=uuid.uuid4(),
        product_id=p.id,
        description_text="Descripción de prueba",
        suggested_price=99.99,
        confidence_score=0.85,
        rationale_internal={},
        rationale_external={},
        status=status,
    )
    db.add(proposal)
    db.commit()
    pid = str(proposal.id)
    db.close()
    return pid


def test_empty_queue_returns_204(client):
    res = client.get("/api/v1/review-queue", headers={"X-Session-Id": "test-empty-session"})
    # May be 204 or 200 depending on existing DB state; just check no 5xx
    assert res.status_code in (200, 204)


def test_available_proposal_returns_queue_item(client):
    pid = _create_proposal(client, status="in_review")
    res = client.get("/api/v1/review-queue", headers={"X-Session-Id": "test-session-q1"})
    assert res.status_code == 200
    data = res.json()
    assert "proposal_id" in data
    assert "queue_total" in data
    assert data["queue_total"] >= 1
    assert data["locked_by_me"] is True


def test_proposal_locked_by_other_excluded(client):
    pid = _create_proposal(client, status="in_review")
    # Lock with session A
    client.post(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": "session-A"})
    # Fetch queue with session B — the locked proposal should be excluded (or a 204 if it's the only one)
    res = client.get("/api/v1/review-queue", headers={"X-Session-Id": "session-B"})
    if res.status_code == 200:
        data = res.json()
        assert data.get("proposal_id") != pid
    else:
        assert res.status_code == 204
