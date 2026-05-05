import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.models.ai_proposal import AIProposal
from backend.src.models.operator_review import OperatorReview
from backend.src.models.product import Product


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def review(self, proposal_id: str, payload: dict) -> OperatorReview:
        proposal_uuid = uuid.UUID(proposal_id)
        proposal = self.db.scalar(select(AIProposal).where(AIProposal.id == proposal_uuid))
        if proposal is None:
            raise ValueError("proposal_not_found")

        review = OperatorReview(
            proposal_id=proposal.id,
            operator_id=payload["operator_id"],
            decision=payload["decision"],
            edited_description_text=payload.get("edited_description"),
            edited_price=payload.get("edited_price"),
            reject_reason=payload.get("reject_reason"),
            notes=payload.get("notes"),
        )
        next_status = "approved" if payload["decision"] == "approve" else "rejected" if payload["decision"] == "reject" else "in_review"
        proposal.status = next_status

        product = self.db.scalar(select(Product).where(Product.id == proposal.product_id))
        if product:
            product.status = "export_ready" if next_status == "approved" else next_status

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review
