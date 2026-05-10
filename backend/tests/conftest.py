import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ["LLM_STUB"] = "true"  # Always use stub in tests

from backend.src.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def cleanup_db():
    yield
    db_file = Path("test.db")
    if db_file.exists():
        try:
            db_file.unlink()
        except PermissionError:
            pass


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
