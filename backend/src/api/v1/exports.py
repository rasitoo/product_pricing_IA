from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.services.export_service import ExportService

router = APIRouter(prefix="/products", tags=["exports"])


@router.post("/{product_id}/export")
def export_product(product_id: str, db: Session = Depends(get_db)):
    try:
        draft = ExportService(db).export(product_id)
    except PermissionError:
        raise HTTPException(status_code=412, detail="human_approval_required")
    return {
        "product_id": str(draft.product_id),
        "export_id": str(draft.id),
        "format": draft.export_format,
        "status": draft.status,
        "download_url": f"/exports/{draft.id}",
    }
