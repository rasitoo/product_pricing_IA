import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.models.base import Base


class AIProposal(Base):
    __tablename__ = "ai_proposals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    description_text: Mapped[str] = mapped_column(String, nullable=False)
    suggested_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    suggested_price_min: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    suggested_price_max: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    confidence_score: Mapped[float] = mapped_column(nullable=False)
    rationale_internal: Mapped[dict] = mapped_column(JSON, default=dict)
    rationale_external: Mapped[dict] = mapped_column(JSON, default=dict)
    expected_days_to_sell: Mapped[int | None] = mapped_column(nullable=True)
    model_name: Mapped[str] = mapped_column(String(100), default="mock-model")
    prompt_version: Mapped[str] = mapped_column(String(50), default="v1")
    status: Mapped[str] = mapped_column(String(50), default="proposed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
