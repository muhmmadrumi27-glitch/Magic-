from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "keyaz_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_max_tasks_per_child=100,
    task_track_started=True,
)
