import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.models.ai_proposal import AIProposal
from backend.src.models.publication_draft import PublicationDraft


class ExportService:
    def __init__(self, db: Session):
        self.db = db

    def export(self, product_id: str) -> PublicationDraft:
        product_uuid = uuid.UUID(product_id)
        proposal = self.db.scalar(
            select(AIProposal).where(AIProposal.product_id == product_uuid).order_by(AIProposal.created_at.desc())
        )
        if proposal is None or proposal.status != "approved":
            raise PermissionError("human_approval_required")

        draft = PublicationDraft(
            product_id=proposal.product_id,
            proposal_id=proposal.id,
            export_format="json",
            payload={
                "title": "draft listing",
                "description": proposal.description_text,
                "price": float(proposal.suggested_price),
            },
            status="ready",
        )
        self.db.add(draft)
        self.db.commit()
        self.db.refresh(draft)
        return draft
