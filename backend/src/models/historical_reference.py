import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.models.base import Base


class HistoricalReference(Base):
    __tablename__ = "historical_references"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    comparable_product_id: Mapped[str] = mapped_column(String(255), nullable=False)
    sold_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    sold_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    condition_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    similarity_score: Mapped[float | None] = mapped_column(nullable=True)
