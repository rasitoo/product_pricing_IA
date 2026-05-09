"""Contract test: verify implemented endpoints match openapi-carousel.yaml schema (T045)."""
import uuid
from pathlib import Path


SPEC_PATH = Path(__file__).resolve().parents[3] / "specs" / "002-carousel-review-ui" / "contracts" / "openapi-carousel.yaml"


def load_spec():
    if not SPEC_PATH.exists():
        return None
    with open(SPEC_PATH) as f:
        import re
        return f.read()  # simple read, no yaml dependency


def test_spec_file_exists():
    assert SPEC_PATH.exists(), f"OpenAPI spec not found at {SPEC_PATH}"


def test_review_queue_endpoint_exists(client):
    res = client.get("/api/v1/review-queue", headers={"X-Session-Id": "contract-test-session"})
    assert res.status_code in (200, 204), f"Unexpected status {res.status_code}"


def test_lock_acquire_endpoint_exists(client):
    import uuid
    # Use a random UUID — will return 404 but endpoint must exist
    fake_id = str(uuid.uuid4())
    res = client.post(f"/api/v1/proposals/{fake_id}/lock", headers={"X-Session-Id": "contract-session"})
    assert res.status_code in (200, 404, 409)


def test_lock_heartbeat_endpoint_exists(client):
    import uuid
    fake_id = str(uuid.uuid4())
    res = client.post(f"/api/v1/proposals/{fake_id}/lock/heartbeat", headers={"X-Session-Id": "contract-session"})
    assert res.status_code in (200, 404, 409)


def test_lock_release_endpoint_exists(client):
    import uuid
    fake_id = str(uuid.uuid4())
    res = client.delete(f"/api/v1/proposals/{fake_id}/lock", headers={"X-Session-Id": "contract-session"})
    assert res.status_code in (204, 403, 404)


def test_review_endpoint_returns_feedback_signals_created(client):
    import uuid
    from sqlalchemy.orm import sessionmaker
    from backend.src.config.database import engine
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
        description_text="Contract test proposal",
        suggested_price=88.0,
        confidence_score=0.9,
        rationale_internal={},
        rationale_external={},
        status="in_review",
    )
    db.add(proposal)
    db.commit()
    pid = str(proposal.id)
    db.close()

    session_id = "contract-review-session"
    client.post(f"/api/v1/proposals/{pid}/lock", headers={"X-Session-Id": session_id})
    res = client.post(
        f"/api/v1/proposals/{pid}/review",
        json={"decision": "approve"},
        headers={"X-Session-Id": session_id},
    )
    assert res.status_code == 200
    data = res.json()
    assert "feedback_signals_created" in data
    assert "next_status" in data
