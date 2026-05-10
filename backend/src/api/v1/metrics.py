from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.services.llm_metrics_service import LLMMetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/llm")
def get_llm_metrics(db: Session = Depends(get_db)):
    return LLMMetricsService(db).summarize()
