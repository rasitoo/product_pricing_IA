import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.models.ai_proposal import AIProposal
from backend.src.models.feedback_signal import FeedbackSignal
from backend.src.models.operator_review import OperatorReview
from backend.src.models.product import Product
from backend.src.services.review_lock_service import ReviewLockService


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def review(self, proposal_id: str, payload: dict, session_id: str | None = None) -> tuple[OperatorReview, list[FeedbackSignal]]:
        proposal_uuid = uuid.UUID(proposal_id)
        proposal = self.db.scalar(select(AIProposal).where(AIProposal.id == proposal_uuid))
        if proposal is None:
            raise ValueError("proposal_not_found")

        # Validate lock ownership when session_id is provided
        if session_id is not None:
            lock_svc = ReviewLockService(self.db)
            try:
                lock_svc.renew(proposal_uuid, session_id)
            except ValueError as exc:
                if "not_found" in str(exc):
                    raise ValueError("lock_required")
                raise ValueError("lock_conflict")

        decision = payload["decision"]

        # Validate edit decision has at least one modified field
        if decision == "edit":
            edited_description = payload.get("edited_description")
            edited_price = payload.get("edited_price")
            has_description_change = (
                edited_description is not None
                and edited_description != proposal.description_text
            )
            has_price_change = (
                edited_price is not None
                and float(edited_price) != float(proposal.suggested_price)
            )
            if not has_description_change and not has_price_change:
                raise ValueError("edit_no_changes")

        review = OperatorReview(
            proposal_id=proposal.id,
            operator_id=payload.get("operator_id") or session_id or "anonymous",
            decision=decision,
            edited_description_text=payload.get("edited_description"),
            edited_price=payload.get("edited_price"),
            reject_reason=payload.get("reject_reason"),
            notes=payload.get("notes"),
        )
        self.db.add(review)
        self.db.flush()  # get review.id before creating signals

        feedback_signals: list[FeedbackSignal] = []
        if decision == "edit":
            edited_description = payload.get("edited_description")
            edited_price = payload.get("edited_price")
            if (
                edited_description is not None
                and edited_description != proposal.description_text
            ):
                sig = FeedbackSignal(
                    proposal_id=proposal.id,
                    review_id=review.id,
                    field_name="description_text",
                    original_value=str(proposal.description_text),
                    corrected_value=str(edited_description),
                )
                self.db.add(sig)
                feedback_signals.append(sig)
            if (
                edited_price is not None
                and float(edited_price) != float(proposal.suggested_price)
            ):
                sig = FeedbackSignal(
                    proposal_id=proposal.id,
                    review_id=review.id,
                    field_name="suggested_price",
                    original_value=str(proposal.suggested_price),
                    corrected_value=str(edited_price),
                )
                self.db.add(sig)
                feedback_signals.append(sig)

        # Update proposal and product status
        if decision == "approve":
            proposal.status = "approved"
            next_product_status = "approved"
        elif decision == "reject":
            proposal.status = "rejected"
            next_product_status = "rejected"
        else:  # edit
            proposal.status = "modified_pending_reapproval"
            next_product_status = "in_review"

        product = self.db.scalar(select(Product).where(Product.id == proposal.product_id))
        if product:
            product.status = next_product_status

        self.db.commit()
        self.db.refresh(review)

        # Release lock after successful review
        if session_id is not None:
            try:
                ReviewLockService(self.db).release(proposal_uuid, session_id)
            except ValueError:
                pass  # Lock already gone is acceptable

        return review, feedback_signals

