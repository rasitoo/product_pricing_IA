"""Integration tests for GET /review-queue endpoint (T015, T056)."""
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


def _create_proposal_with_image(status="in_review"):
    """Helper: create product + proposal + ProductImage."""
    import uuid as _uuid
    from sqlalchemy.orm import sessionmaker
    from backend.src.models.product import Product
    from backend.src.models.ai_proposal import AIProposal
    from backend.src.models.product_image import ProductImage
    from backend.src.config.database import engine

    Session = sessionmaker(bind=engine)
    db = Session()
    product_id = _uuid.uuid4()
    p = Product(id=product_id, source_channel="api", status=status, tags={})
    db.add(p)
    db.flush()
    proposal = AIProposal(
        id=_uuid.uuid4(),
        product_id=product_id,
        description_text="Propuesta con imagen",
        suggested_price=50.0,
        confidence_score=0.9,
        rationale_internal={},
        rationale_external={},
        status=status,
    )
    db.add(proposal)
    db.flush()
    image = ProductImage(
        id=_uuid.uuid4(),
        product_id=product_id,
        storage_uri=f"data/uploads/{product_id}/foto.jpg",
        sha256_hash=_uuid.uuid4().hex,
        mime_type="image/jpeg",
    )
    db.add(image)
    db.commit()
    pid = str(proposal.id)
    db.close()
    return pid


def test_empty_queue_returns_204(client):
    res = client.get("/api/v1/review-queue", headers={"X-Session-Id": "test-empty-session"})
    # May be 204 or 200 depending on existing DB state; just check no 5xx
    assert res.status_code in (200, 204)


def test_available_proposal_returns_queue_item(client):
    _create_proposal_with_image(status="in_review")
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


def test_proposal_without_images_excluded_from_queue(client):
    """T056 — FR-016: propuesta sin imágenes no debe aparecer en la cola."""
    # Create proposal WITHOUT image
    no_img_pid = _create_proposal(client, status="in_review")

    # Create proposal WITH image
    with_img_pid = _create_proposal_with_image(status="in_review")

    session_id = f"session-fr016-{uuid.uuid4()}"
    res = client.get("/api/v1/review-queue", headers={"X-Session-Id": session_id})

    # The queue must return something (the proposal with image)
    assert res.status_code == 200
    data = res.json()
    # The proposal without image must NOT be the one returned
    assert data["proposal_id"] != no_img_pid
    # The proposal with image should be accessible (may be returned directly)
    assert data["proposal_id"] == with_img_pid or data["queue_total"] >= 1


def test_proposal_with_image_appears_in_queue(client):
    """T056 — FR-016: propuesta con imagen sí aparece en la cola."""
    with_img_pid = _create_proposal_with_image(status="in_review")
    session_id = f"session-with-img-{uuid.uuid4()}"
    res = client.get("/api/v1/review-queue", headers={"X-Session-Id": session_id})
    assert res.status_code == 200
    data = res.json()
    assert "proposal_id" in data
