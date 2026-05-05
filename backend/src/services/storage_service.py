import base64
import hashlib
from pathlib import Path

from backend.src.config.settings import get_settings


class StorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.root = Path(self.settings.image_storage_path)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_photo(self, product_id: str, filename: str, content_b64: str) -> tuple[str, str]:
        # Strip data URI prefix if present (e.g. "data:image/jpeg;base64,...")
        if "," in content_b64:
            content_b64 = content_b64.split(",", 1)[1]
        # Add padding if needed
        content_b64 += "=" * (-len(content_b64) % 4)
        binary = base64.b64decode(content_b64)
        digest = hashlib.sha256(binary).hexdigest()
        target_dir = self.root / str(product_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / filename
        target_file.write_bytes(binary)
        return str(target_file), digest
