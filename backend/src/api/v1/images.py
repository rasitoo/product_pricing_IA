"""Image management endpoints: list, upload (multipart) and delete product images."""
import hashlib
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.models.product import Product
from backend.src.models.product_image import ProductImage
from backend.src.repositories.product_repository import ProductRepository
from backend.src.services.storage_service import StorageService

router = APIRouter(prefix="/products", tags=["images"])

_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}
_MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def _parse_product_uuid(product_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="invalid_product_id")


@router.get("/{product_id}/images")
def list_images(product_id: str, db: Session = Depends(get_db)):
    """Return all images stored for a product."""
    product_uuid = _parse_product_uuid(product_id)
    repo = ProductRepository(db)
    images = repo.get_images_for_product(product_uuid)
    storage = StorageService()
    return [
        {
            "image_id": str(img.id),
            "url": storage.public_url(img.storage_uri),
            "thumbnail_url": storage.public_url(img.storage_uri),
            "mime_type": img.mime_type,
            "sha256_hash": img.sha256_hash,
            "quality_score": img.quality_score,
            "created_at": img.created_at.isoformat(),
        }
        for img in images
    ]


@router.post("/{product_id}/images", status_code=201)
async def upload_images(
    product_id: str,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Upload one or more images for an existing product (multipart/form-data)."""
    product_uuid = _parse_product_uuid(product_id)

    product = db.get(Product, product_uuid)
    if product is None:
        raise HTTPException(status_code=404, detail="product_not_found")

    if not files:
        raise HTTPException(status_code=422, detail="no_files_provided")

    storage = StorageService()
    created_ids: list[str] = []

    for file in files:
        mime = file.content_type or "image/jpeg"
        if mime not in _ALLOWED_MIME:
            raise HTTPException(
                status_code=415,
                detail=f"unsupported_media_type: {mime}. Allowed: {sorted(_ALLOWED_MIME)}",
            )

        content = await file.read()
        if len(content) > _MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="file_too_large: max 20 MB per image")

        digest = hashlib.sha256(content).hexdigest()

        # Skip exact duplicates within the same product
        existing = db.query(ProductImage).filter_by(
            sha256_hash=digest, product_id=product_uuid
        ).first()
        if existing:
            continue

        safe_filename = f"{uuid.uuid4()}_{file.filename or 'image.jpg'}"
        storage_uri = storage.save_photo_binary(product_id, safe_filename, content)

        img = ProductImage(
            product_id=product_uuid,
            storage_uri=storage_uri,
            sha256_hash=digest,
            mime_type=mime,
        )
        db.add(img)
        db.flush()
        created_ids.append(str(img.id))

    db.commit()
    return {"uploaded": len(created_ids), "image_ids": created_ids}


@router.delete("/{product_id}/images/{image_id}", status_code=204)
def delete_image(product_id: str, image_id: str, db: Session = Depends(get_db)):
    """Delete a specific image from a product."""
    product_uuid = _parse_product_uuid(product_id)
    try:
        img_uuid = uuid.UUID(image_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="invalid_image_id")

    img = db.get(ProductImage, img_uuid)
    if img is None or img.product_id != product_uuid:
        raise HTTPException(status_code=404, detail="image_not_found")

    StorageService().delete_photo(img.storage_uri)
    db.delete(img)
    db.commit()
