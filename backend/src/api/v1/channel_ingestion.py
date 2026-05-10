from fastapi import APIRouter
from pydantic import BaseModel

from backend.src.services.channel_adapter_service import ChannelAdapterService

router = APIRouter(prefix="/channel-ingestion", tags=["channels"])


class ChannelIn(BaseModel):
    source_channel: str
    photos: list[dict]
    external_reference: str | None = None


@router.post("/normalize")
def normalize(payload: ChannelIn):
    return ChannelAdapterService().normalize(payload.model_dump())
