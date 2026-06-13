"""Celery application configuration and initialization.

This module initializes the Celery application used for background tasks
and configures the Celery beat schedule.
"""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "atomquest",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.presence_tasks", "app.tasks.recording_tasks"],
)

celery_app.conf.beat_schedule = {
    "check-expired-presence-every-10-seconds": {
        "task": "app.tasks.presence_tasks.check_expired_presence",
        "schedule": 10.0,
    },
}
celery_app.conf.timezone = "UTC"

# Import all models to ensure SQLAlchemy mapper initialization doesn't fail due to missing relationships
import app.modules.auth.models
import app.modules.sessions.models
import app.modules.participants.models
import app.modules.chat.models
import app.modules.recordings.models
