import asyncio

import structlog
from celery import shared_task

from app.core.livekit import livekit_service
from app.db.database import SessionLocal
from app.modules.recordings import repositories as recording_repos
from app.modules.recordings.models import RecordingStatus

logger = structlog.get_logger()


async def _poll_egress_completion(recording_id: int, egress_id: str):
    """Async helper to poll LiveKit egress info periodically.

    Args:
        recording_id (int): The database record ID of the recording.
        egress_id (str): The LiveKit generated egress ID.

    Returns:
        None
    """
    lkapi = livekit_service.get_api()

    # We poll every 5 seconds for up to 10 minutes
    for _ in range(120):
        try:
            from livekit.api import ListEgressRequest

            # livekit_api currently only has list_egress or we can use egress_id in it
            res = await lkapi.egress.list_egress(ListEgressRequest(egress_id=egress_id))
            if res.items:
                info = res.items[0]
                status = info.status
                # egress status enum:
                # 0: EGRESS_STARTING, 1: EGRESS_ACTIVE, 2: EGRESS_ENDING, 3: EGRESS_COMPLETE, 4: EGRESS_FAILED, 5: EGRESS_ABORTED, 6: EGRESS_LIMIT_REACHED
                if status in [3]:  # EGRESS_COMPLETE
                    # Mark complete in DB
                    db = SessionLocal()
                    try:
                        file_path = ""
                        if info.file_results:
                            file_path = info.file_results[0].filename
                        recording_repos.update_status(
                            db, recording_id, RecordingStatus.ready, file_path=file_path
                        )
                        logger.info(
                            "egress_completed",
                            recording_id=recording_id,
                            egress_id=egress_id,
                        )
                    finally:
                        db.close()
                    return
                elif status in [4, 5, 6]:  # FAILED, ABORTED, LIMIT_REACHED
                    db = SessionLocal()
                    try:
                        recording_repos.update_status(
                            db, recording_id, RecordingStatus.failed
                        )
                        logger.error(
                            "egress_failed",
                            recording_id=recording_id,
                            egress_id=egress_id,
                            status=status,
                            error=info.error,
                        )
                    finally:
                        db.close()
                    return
        except Exception as e:
            logger.error("poll_egress_error", error=str(e))

        await asyncio.sleep(5)


@shared_task(name="app.tasks.recording_tasks.monitor_egress_completion")
def monitor_egress_completion(recording_id: int, egress_id: str):
    """Celery task to monitor the completion of a LiveKit Egress recording.

    Args:
        recording_id (int): The database record ID of the recording.
        egress_id (str): The LiveKit generated egress ID.

    Returns:
        None
    """
    asyncio.run(_poll_egress_completion(recording_id, egress_id))
