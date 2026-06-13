"""
Redis connection pool for caching and Celery broker.
"""
import redis

from app.core.config import settings

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)

