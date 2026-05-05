import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.models.base import Base


class PublicationDraft(Base):
    __tablename__ = "publication_drafts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    proposal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_proposals.id"), nullable=False)
    export_format: Mapped[str] = mapped_column(Enum("json", "csv", "html", name="export_format"), default="json")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(Enum("ready", "exported", "published_external", name="publication_status"), default="ready")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
