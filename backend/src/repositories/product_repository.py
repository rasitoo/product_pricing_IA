import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.models.ai_proposal import AIProposal
from backend.src.models.product import Product


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
