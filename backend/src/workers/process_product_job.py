import uuid
from sqlalchemy import select

from backend.src.config.database import SessionLocal
from backend.src.models.ai_proposal import AIProposal
from backend.src.models.product import Product
from backend.src.services.pricing_service import PricingService
from backend.src.workers.celery_app import celery_app


@celery_app.task(name="process_product")
def process_product(product_id: str, photos: list[dict]) -> str:
    db = SessionLocal()
    try:
        product_uuid = uuid.UUID(product_id)
        service = PricingService()
        proposal_data = __import__("asyncio").run(service.build_proposal(photos, query="generic-product"))
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
