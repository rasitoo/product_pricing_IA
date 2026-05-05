import base64

from backend.src.services.storage_service import StorageService


def test_image_hash_is_stable(tmp_path, monkeypatch):
    monkeypatch.setenv("IMAGE_STORAGE_PATH", str(tmp_path))
    svc = StorageService()
    payload = base64.b64encode(b"same-content").decode()
    _, h1 = svc.save_photo("p1", "a.jpg", payload)
    _, h2 = svc.save_photo("p1", "b.jpg", payload)
    assert h1 == h2
