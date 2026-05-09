import asyncio
import uuid

from sqlalchemy import select, desc

from backend.src.config.database import SessionLocal
from backend.src.models.ai_proposal import AIProposal
from backend.src.models.feedback_signal import FeedbackSignal
from backend.src.models.historical_reference import HistoricalReference
from backend.src.models.product import Product
from backend.src.models.product_image import ProductImage
from backend.src.services.pricing_service import PricingService
from backend.src.workers.celery_app import celery_app


def _build_context(db, product_uuid: uuid.UUID) -> dict:
    """Collect enrichment context from the DB: feedback signals and historical refs."""
    # Recent operator corrections (all products, last 20) to teach the LLM
    feedback_rows = db.scalars(
        select(FeedbackSignal)
        .order_by(desc(FeedbackSignal.created_at))
        .limit(20)
    ).all()

    # Historical sales in our platform (most recent, limit 10)
    hist_rows = db.scalars(
        select(HistoricalReference)
        .order_by(desc(HistoricalReference.sold_at))
        .limit(10)
    ).all()

    return {
        "feedback_signals": [
            {
                "field_name": f.field_name,
                "original_value": f.original_value,
                "corrected_value": f.corrected_value,
            }
            for f in feedback_rows
        ],
        "historical_refs": [
            {
                "sold_price": float(h.sold_price),
                "condition_label": h.condition_label,
                "similarity_score": h.similarity_score,
            }
            for h in hist_rows
        ],
    }


@celery_app.task(name="process_product")
def process_product(product_id: str, photos: list[dict]) -> str:
    db = SessionLocal()
    try:
        product_uuid = uuid.UUID(product_id)

        # Enrich photos with storage_uri from the DB so the LLM can load images from disk
        images = db.scalars(
            select(ProductImage).where(ProductImage.product_id == product_uuid)
        ).all()
        uri_map = {img.sha256_hash: img.storage_uri for img in images}

        enriched_photos: list[dict] = []
        for photo in photos:
            entry: dict = dict(photo)
            # Match by sha256 (computed during upload) or just attach first image
            if images and "storage_uri" not in entry:
                entry["storage_uri"] = images[len(enriched_photos) % len(images)].storage_uri
            enriched_photos.append(entry)

        if not enriched_photos and images:
            # Fallback: build photo list from stored images (re-analysis case)
            enriched_photos = [{"storage_uri": img.storage_uri, "filename": ""} for img in images]

        context = _build_context(db, product_uuid)

        service = PricingService()
        proposal_data = asyncio.run(
            service.build_proposal(enriched_photos, query="", context=context)
        )

        proposal = AIProposal(
            product_id=product_uuid,
            description_text=proposal_data["description"],
            suggested_price=proposal_data["suggested_price"],
            suggested_price_min=proposal_data["suggested_price_min"],
            suggested_price_max=proposal_data["suggested_price_max"],
            confidence_score=proposal_data["confidence_score"],
            rationale_internal=proposal_data["rationale_internal"],
            rationale_external=proposal_data["rationale_external"],
            status="proposed",
        )
        db.add(proposal)

        product = db.scalar(select(Product).where(Product.id == product_uuid))
        if product:
            product.status = "proposed"

        db.commit()
        db.refresh(proposal)
        return str(proposal.id)
    finally:
        db.close()
