import uuid
from datetime import datetime

from sqlalchemy import select, case, func, exists
from sqlalchemy.orm import Session

from backend.src.models.ai_proposal import AIProposal
from backend.src.models.product import Product
from backend.src.models.product_image import ProductImage
from backend.src.models.review_lock import ReviewLock


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, source_channel: str = "api") -> Product:
        product = Product(source_channel=source_channel, status="analyzing")
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_proposal(self, proposal_id: str) -> AIProposal | None:
        stmt = select(AIProposal).where(AIProposal.id == uuid.UUID(proposal_id))
        return self.db.scalar(stmt)

    def save_proposal(self, proposal: AIProposal) -> AIProposal:
        self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)
        return proposal

    def get_review_queue(self, session_id: str) -> dict | None:
        """Return the next proposal available for review.

        Priority: modified_pending_reapproval first, then created_at ASC.
        Excludes proposals locked by a different active session.
        Returns a dict with proposal data, queue_total, and queue_position, or None if empty.
        """
        now = datetime.utcnow()

        # Subquery: proposal_ids locked by other sessions
        locked_by_others = select(ReviewLock.proposal_id).where(
            ReviewLock.expires_at > now,
            ReviewLock.session_id != session_id,
        )

        # Subquery: proposal_ids that have at least one image (FR-016)
        has_image = select(ProductImage.product_id).where(
            ProductImage.product_id == AIProposal.product_id
        )

        # Count total available proposals
        count_stmt = (
            select(func.count())
            .select_from(AIProposal)
            .where(
                AIProposal.status.in_(["in_review", "modified_pending_reapproval"]),
                AIProposal.id.not_in(locked_by_others),
                exists(has_image),
            )
        )
        total = self.db.scalar(count_stmt) or 0
        if total == 0:
            return None

        # Priority ordering: modified_pending_reapproval = 0, others = 1
        priority = case(
            (AIProposal.status == "modified_pending_reapproval", 0),
            else_=1,
        )
        stmt = (
            select(AIProposal)
            .where(
                AIProposal.status.in_(["in_review", "modified_pending_reapproval"]),
                AIProposal.id.not_in(locked_by_others),
                exists(has_image),
            )
            .order_by(priority, AIProposal.created_at)
            .limit(1)
        )
        proposal = self.db.scalar(stmt)
        if proposal is None:
            return None

        product = self.db.scalar(select(Product).where(Product.id == proposal.product_id))
        images = self.db.scalars(
            select(ProductImage).where(ProductImage.product_id == proposal.product_id)
        ).all()

        return {
            "proposal": proposal,
            "product": product,
            "images": images,
            "queue_total": total,
            "queue_position": 1,
        }

    def get_images_for_product(self, product_id: uuid.UUID) -> list:
        return list(
            self.db.scalars(select(ProductImage).where(ProductImage.product_id == product_id)).all()
        )
