from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.config.settings import get_settings
from backend.src.repositories.product_repository import ProductRepository
from backend.src.services.review_lock_service import ReviewLockService

router = APIRouter(prefix="/review-queue", tags=["review-queue"])
_settings = get_settings()


def _image_url(storage_uri: str) -> str:
    filename = storage_uri.split("/")[-1]
    return f"/uploads/{filename}"


@router.get("")
def get_next_queue_item(
    response: Response,
    x_session_id: str = Header(..., alias="X-Session-Id"),
    db: Session = Depends(get_db),
):
    """Return the next proposal available for review and acquire its lock."""
    repo = ProductRepository(db)
    result = repo.get_review_queue(session_id=x_session_id)

    if result is None:
        return Response(status_code=204)

    proposal = result["proposal"]
    images = result["images"]

    # Acquire lock for the returned proposal
    try:
        lock = ReviewLockService(db).acquire(proposal.id, x_session_id)
    except ValueError:
        # Lock conflict — queue already returned a proposal not locked by others;
        # this edge case means it was just claimed concurrently.
        return Response(status_code=204)

    image_list = [
        {"url": _image_url(img.storage_uri), "thumbnail_url": _image_url(img.storage_uri)}
        for img in images
    ]

    return {
        "proposal_id": str(proposal.id),
        "product_id": str(proposal.product_id),
        "description": proposal.description_text,
        "suggested_price": float(proposal.suggested_price),
        "suggested_price_min": float(proposal.suggested_price_min or 0),
        "suggested_price_max": float(proposal.suggested_price_max or 0),
        "confidence_score": proposal.confidence_score,
        "status": proposal.status,
        "images": image_list,
        "queue_total": result["queue_total"],
        "queue_position": result["queue_position"],
        "locked_by_me": True,
        "lock_expires_at": lock.expires_at.isoformat(),
    }
