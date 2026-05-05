import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.models.base import Base


class ExternalComparable(Base):
    __tablename__ = "external_comparables"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    proposal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_proposals.id"), nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    listing_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    listed_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
