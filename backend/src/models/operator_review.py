import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.models.base import Base


class OperatorReview(Base):
    __tablename__ = "operator_reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    proposal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_proposals.id"), nullable=False)
    operator_id: Mapped[str] = mapped_column(String(255), nullable=False)
    decision: Mapped[str] = mapped_column(Enum("approve", "reject", "edit", name="review_decision"), nullable=False)
    edited_description_text: Mapped[str | None] = mapped_column(String, nullable=True)
    edited_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
