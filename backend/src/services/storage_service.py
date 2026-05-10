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
        """Save a base64-encoded photo. Returns (storage_uri, sha256_hash)."""
        if "," in content_b64:
            content_b64 = content_b64.split(",", 1)[1]
        content_b64 += "=" * (-len(content_b64) % 4)
        binary = base64.b64decode(content_b64)
        digest = hashlib.sha256(binary).hexdigest()
        target_dir = self.root / str(product_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / filename
        target_file.write_bytes(binary)
        return str(target_file), digest

    def save_photo_binary(self, product_id: str, filename: str, content: bytes) -> str:
        """Save raw binary photo content. Returns storage_uri."""
        target_dir = self.root / str(product_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / filename
        target_file.write_bytes(content)
        return str(target_file)

    def public_url(self, storage_uri: str) -> str:
        """Convert a storage_uri to a public URL path under /uploads/."""
        path = Path(storage_uri)
        try:
            rel = path.relative_to(self.root)
            return f"/uploads/{rel.as_posix()}"
        except ValueError:
            return f"/uploads/{path.name}"

    def delete_photo(self, storage_uri: str) -> None:
        """Delete a photo file from disk (best-effort, no error if missing)."""
        path = Path(storage_uri)
        path.unlink(missing_ok=True)
