"""Integration tests for lock endpoints (T027)."""
import uuid


def _create_proposal_in_review(engine):
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
        description_text="Lock test",
        suggested_price=50.0,
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


def test_acquire_lock_returns_expires_at(client):
    from backend.src.config.database import engine
    pid = _create_proposal_in_review(engine)
    res = client.post(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": "lock-session-1"})
    assert res.status_code == 200
    data = res.json()
    assert "expires_at" in data


def test_heartbeat_renews_lock(client):
    from backend.src.config.database import engine
    pid = _create_proposal_in_review(engine)
    client.post(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": "lock-session-2"})
    res = client.post(f"/api/v1/proposals/{pid}/lock/heartbeat", headers={"X-Session-Id": "lock-session-2"})
    assert res.status_code == 200
    assert "expires_at" in res.json()


def test_release_returns_204(client):
    from backend.src.config.database import engine
    pid = _create_proposal_in_review(engine)
    client.post(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": "lock-session-3"})
    res = client.delete(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": "lock-session-3"})
    assert res.status_code == 204


def test_release_other_session_returns_403(client):
    from backend.src.config.database import engine
    pid = _create_proposal_in_review(engine)
    client.post(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": "lock-owner"})
    res = client.delete(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": "lock-intruder"})
    assert res.status_code == 403
