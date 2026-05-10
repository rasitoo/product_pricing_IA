from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.src.config.settings import get_settings
from backend.src.models.base import Base

settings = get_settings()
engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
