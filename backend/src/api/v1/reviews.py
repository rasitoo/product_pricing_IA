from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.services.review_service import ReviewService

router = APIRouter(prefix="/proposals", tags=["reviews"])


class ReviewIn(BaseModel):
    decision: str
    operator_id: str | None = None
    edited_description: str | None = None
    edited_price: float | None = None
    reject_reason: str | None = None
    notes: str | None = None


@router.post("/{proposal_id}/review")
def review_proposal(
    proposal_id: str,
    payload: ReviewIn,
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
    db: Session = Depends(get_db),
):
    try:
        review, feedback_signals = ReviewService(db).review(
            proposal_id, payload.model_dump(), session_id=x_session_id
        )
    except ValueError as exc:
        msg = str(exc)
        if msg == "proposal_not_found":
            raise HTTPException(status_code=404, detail=msg)
        if msg in ("lock_required", "lock_conflict"):
            raise HTTPException(status_code=409, detail=msg)
        if msg == "edit_no_changes":
            raise HTTPException(status_code=422, detail="edit requires at least one changed field")
        raise HTTPException(status_code=400, detail=msg)

    if review.decision == "approve":
        next_status = "approved"
    elif review.decision == "reject":
        next_status = "rejected"
    else:
        next_status = "modified_pending_reapproval"

    return {
        "review_id": str(review.id),
        "proposal_id": str(review.proposal_id),
        "decision": review.decision,
        "reviewed_at": review.created_at.isoformat(),
        "next_status": next_status,
        "feedback_signals_created": len(feedback_signals),
    }

