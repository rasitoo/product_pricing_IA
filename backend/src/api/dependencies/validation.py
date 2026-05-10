from fastapi import HTTPException

MAX_PHOTOS_PER_PRODUCT = 5
MAX_BASE64_SIZE_CHARS = 8_000_000


def validate_photo_payload(photos: list[dict]) -> None:
    if not photos:
        raise HTTPException(status_code=422, detail="at_least_one_photo_required")
    if len(photos) > MAX_PHOTOS_PER_PRODUCT:
        raise HTTPException(status_code=422, detail="too_many_photos")
    for photo in photos:
        content = photo.get("content_base64", "")
        if len(content) > MAX_BASE64_SIZE_CHARS:
            raise HTTPException(status_code=413, detail="photo_payload_too_large")
