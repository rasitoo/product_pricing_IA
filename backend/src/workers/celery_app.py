from celery import Celery

from backend.src.config.settings import get_settings

settings = get_settings()
celery_app = Celery("resale_pricing", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_default_queue = "pricing"
