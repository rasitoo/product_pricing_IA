from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.repositories.product_repository import ProductRepository

router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.get("/{proposal_id}")
def get_proposal(proposal_id: str, db: Session = Depends(get_db)):
    proposal = ProductRepository(db).get_proposal(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="proposal_not_found")
    return {
        "proposal_id": str(proposal.id),
        "product_id": str(proposal.product_id),
        "description": proposal.description_text,
        "suggested_price": float(proposal.suggested_price),
        "suggested_price_min": float(proposal.suggested_price_min or 0),
        "suggested_price_max": float(proposal.suggested_price_max or 0),
        "confidence_score": proposal.confidence_score,
        "rationale_internal": proposal.rationale_internal,
        "rationale_external": proposal.rationale_external,
        "status": proposal.status,
    }
