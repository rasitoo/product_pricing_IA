import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_channel: Mapped[str] = mapped_column(Enum("api", "whatsapp", "telegram", name="source_channel"), default="api")
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(
        Enum("draft", "analyzing", "proposed", "in_review", "approved", "rejected", "export_ready", name="product_status"),
        default="draft",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
