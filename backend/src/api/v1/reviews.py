from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.services.review_service import ReviewService

router = APIRouter(prefix="/proposals", tags=["reviews"])


class ReviewIn(BaseModel):
    decision: str
    operator_id: str
    edited_description: str | None = None
    edited_price: float | None = None
    reject_reason: str | None = None
    notes: str | None = None


@router.post("/{proposal_id}/review")
def review_proposal(proposal_id: str, payload: ReviewIn, db: Session = Depends(get_db)):
    try:
        review = ReviewService(db).review(proposal_id, payload.model_dump())
    except ValueError:
        raise HTTPException(status_code=404, detail="proposal_not_found")
    next_status = "approved" if review.decision == "approve" else "rejected" if review.decision == "reject" else "in_review"
    return {
        "review_id": str(review.id),
        "proposal_id": str(review.proposal_id),
        "decision": review.decision,
        "reviewed_at": review.created_at.isoformat(),
        "next_status": next_status,
    }
