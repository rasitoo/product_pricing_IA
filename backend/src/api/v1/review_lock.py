import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.services.review_lock_service import ReviewLockService

router = APIRouter(prefix="/proposals", tags=["review-lock"])


@router.post("/{proposal_id}/lock")
def acquire_lock(
    proposal_id: str,
    x_session_id: str = Header(..., alias="X-Session-Id"),
    db: Session = Depends(get_db),
):
    try:
        lock = ReviewLockService(db).acquire(uuid.UUID(proposal_id), x_session_id)
    except ValueError as exc:
        if "conflict" in str(exc):
            raise HTTPException(status_code=409, detail="lock_conflict")
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "proposal_id": proposal_id,
        "session_id": x_session_id,
        "locked_at": lock.locked_at.isoformat(),
        "expires_at": lock.expires_at.isoformat(),
    }


@router.delete("/{proposal_id}/lock", status_code=204)
def release_lock(
    proposal_id: str,
    x_session_id: str = Header(..., alias="X-Session-Id"),
    db: Session = Depends(get_db),
):
    try:
        ReviewLockService(db).release(uuid.UUID(proposal_id), x_session_id)
    except ValueError as exc:
        if "forbidden" in str(exc):
            raise HTTPException(status_code=403, detail="lock_forbidden")
    return Response(status_code=204)


@router.post("/{proposal_id}/lock/heartbeat")
def heartbeat_lock(
    proposal_id: str,
    x_session_id: str = Header(..., alias="X-Session-Id"),
    db: Session = Depends(get_db),
):
    try:
        lock = ReviewLockService(db).renew(uuid.UUID(proposal_id), x_session_id)
    except ValueError as exc:
        if "not_found" in str(exc):
            raise HTTPException(status_code=404, detail="lock_not_found")
        raise HTTPException(status_code=409, detail="lock_conflict")
    return {
        "proposal_id": proposal_id,
        "expires_at": lock.expires_at.isoformat(),
    }
