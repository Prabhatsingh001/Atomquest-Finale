import time

import redis
import structlog
from celery import shared_task

from app.core.config import settings
from app.db.database import SessionLocal
from app.modules.participants import repositories as participant_repos

logger = structlog.get_logger()

try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.error("redis_connection_failed", error=str(e))
    redis_client = None


def set_online(session_id: int, user_id: int):
    """Mark participant as online, removing them from the offline grace period tracking.

    Args:
        session_id (int): The session ID.
        user_id (int): The user ID.

    Returns:
        None
    """
    if not redis_client:
        return
    try:
        redis_client.zrem("presence:offline_users", f"{session_id}:{user_id}")
        logger.info("participant_online", session_id=session_id, user_id=user_id)
    except Exception as e:
        logger.error("redis_presence_error", error=str(e))


def set_offline(session_id: int, user_id: int):
    """Start the 30s grace period for a disconnected participant.

    Args:
        session_id (int): The session ID.
        user_id (int): The user ID.

    Returns:
        None
    """
    if not redis_client:
        return
    try:
        expiry = time.time() + 30
        redis_client.zadd("presence:offline_users", {f"{session_id}:{user_id}": expiry})
        logger.info("participant_offline_grace", session_id=session_id, user_id=user_id)
    except Exception as e:
        logger.error("redis_presence_error", error=str(e))


@shared_task(name="app.tasks.presence_tasks.check_expired_presence")
def check_expired_presence():
    """Periodic task to sweep offline participants who exceeded their grace period.

    Returns:
        None
    """
    if not redis_client:
        return
    try:
        now = time.time()
        # Find all users whose expiry is in the past
        expired_entries = redis_client.zrangebyscore(
            "presence:offline_users", "-inf", now
        )

        if not expired_entries:
            return

        db = SessionLocal()
        try:
            for entry in expired_entries:
                session_id_str, user_id_str = entry.split(":")
                session_id = int(session_id_str)
                user_id = int(user_id_str)

                # Mark as left in database
                participant_repos.mark_left(db, session_id, user_id)
                logger.info(
                    "participant_grace_expired", session_id=session_id, user_id=user_id
                )

                # Broadcast user left message - Note: In a multi-process setup,
                # this requires Redis PubSub. For MVP, we skip the cross-process broadcast.
                # async_to_sync(manager.broadcast)(session_id, {
                #     "type": "system",
                #     "content": "A user has left the session."
                # })

            # Remove them from the ZSET
            redis_client.zrem("presence:offline_users", *expired_entries)
        finally:
            db.close()

    except Exception as e:
        logger.error("check_expired_presence_error", error=str(e))
