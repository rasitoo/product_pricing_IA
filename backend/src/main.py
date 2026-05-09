from fastapi import FastAPI

from backend.src.api.dependencies.middleware import RequestContextMiddleware, unhandled_exception_handler
from backend.src.api.v1 import channel_ingestion, exports, metrics, products, proposals, review_lock, review_queue, reviews
from backend.src.config.database import init_db
from backend.src.config.settings import get_settings

# Ensure SQLAlchemy models are imported before init_db.
from backend.src.models import (  # noqa: F401
    ai_proposal,
    external_comparable,
    feedback_signal,
    historical_reference,
    llm_metric,
    operator_review,
    product,
    product_image,
    publication_draft,
    review_lock as review_lock_model,
)

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(RequestContextMiddleware)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(products.router, prefix=settings.api_prefix)
app.include_router(proposals.router, prefix=settings.api_prefix)
app.include_router(reviews.router, prefix=settings.api_prefix)
app.include_router(exports.router, prefix=settings.api_prefix)
app.include_router(metrics.router, prefix=settings.api_prefix)
app.include_router(channel_ingestion.router, prefix=settings.api_prefix)
app.include_router(review_queue.router, prefix=settings.api_prefix)
app.include_router(review_lock.router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
