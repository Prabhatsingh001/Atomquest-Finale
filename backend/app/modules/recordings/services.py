import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.livekit import LiveKitService
from app.modules.sessions import repositories as session_repos
from app.tasks.recording_tasks import monitor_egress_completion

from . import repositories as recording_repos
from .models import Recording

RECORDING_DIR = "recordings"

async def start_recording(db: Session, livekit: LiveKitService, session_id: int, agent_id: int) -> Recording:
    """Execute start recording operation.
    
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
    
        Returns:
            Result of the operation.
    """
    session = session_repos.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    if session.agent_id != agent_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to record this session")

    if session.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not active")

    # Generate a unique filename
    filename = f"session_{session_id}_{uuid.uuid4().hex}.mp4"
    file_path = f"/app/recordings/{filename}"

    # Start LiveKit Egress
    try:
        egress_id = await livekit.start_room_composite_egress(session.room_name, file_path)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"LiveKit Egress failed: {str(e)}")

    # Save to database
    recording = recording_repos.create(db, session_id, egress_id)
    
    # Increment metric
    try:
        from app.modules.metrics.services import TOTAL_RECORDINGS
        TOTAL_RECORDINGS.inc()
    except Exception:
        pass

    # Broadcast that recording has started
    try:
        import asyncio

        from app.modules.websocket.manager import manager
        asyncio.create_task(manager.broadcast(session_id, {
            "type": "recording_started",
            "content": "A recording has been started by the agent."
        }))
    except Exception:
        pass
        
    return recording

async def stop_recording(db: Session, livekit: LiveKitService, recording_id: int, agent_id: int) -> Recording:
    """Execute stop recording operation.
    
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
    
        Returns:
            Result of the operation.
    """
    recording = recording_repos.get_by_id(db, recording_id)
    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")

    session = session_repos.get_session(db, recording.session_id)
    if session.agent_id != agent_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if recording.status != "recording":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recording is not active")

    # Stop LiveKit Egress
    try:
        await livekit.stop_egress(recording.livekit_egress_id)
    except Exception:
        # Might already be stopped or failed, proceed anyway
        pass

    from .models import RecordingStatus
    recording = recording_repos.update_status(db, recording.id, RecordingStatus.processing)

    # Dispatch Celery task to monitor completion
    monitor_egress_completion.delay(recording.id, recording.livekit_egress_id)

    return recording
