"""
Celery application for background tasks.
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "atomquest",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "app.tasks.recording_tasks.*": {"queue": "recordings"},
        "app.tasks.presence_tasks.*": {"queue": "presence"},
    },
)

# Auto-discover tasks in the tasks directory
celery_app.autodiscover_tasks(["app.tasks"])
