from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.src.api.dependencies.validation import validate_photo_payload
from backend.src.config.database import get_db
from backend.src.models.product_image import ProductImage
from backend.src.repositories.product_repository import ProductRepository
from backend.src.services.storage_service import StorageService
from backend.src.workers.process_product_job import process_product

router = APIRouter(prefix="/products", tags=["products"])


class PhotoIn(BaseModel):
    filename: str
    content_base64: str


class ProductCreateIn(BaseModel):
    source_channel: str = "api"
    photos: list[PhotoIn]


@router.post("", status_code=202)
def create_product(payload: ProductCreateIn, db: Session = Depends(get_db)):
    validate_photo_payload([p.model_dump() for p in payload.photos])

    repo = ProductRepository(db)
    storage = StorageService()

    product = repo.create_product(source_channel=payload.source_channel)
    for photo in payload.photos:
        uri, digest = storage.save_photo(str(product.id), photo.filename, photo.content_base64)
        db.add(
            ProductImage(
                product_id=product.id,
                storage_uri=uri,
                sha256_hash=digest,
                mime_type="image/jpeg",
            )
        )
    db.commit()

    # Run inline in local/dev to avoid broker dependency during early phases.
    process_product(str(product.id), [p.model_dump() for p in payload.photos])

    return {"product_id": str(product.id), "status": "analyzing", "proposal_id": None}
