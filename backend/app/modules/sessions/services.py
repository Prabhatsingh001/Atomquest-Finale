"""
Business logic for Session management.
"""
import uuid
import structlog
from sqlalchemy.orm import Session as DbSession
from fastapi import HTTPException, status

from app.modules.sessions import repositories
from app.core.livekit import get_livekit

logger = structlog.get_logger()


async def create_session(db: DbSession, title: str, agent_id: int):
    """Create a new session in DB and a room in LiveKit."""
    # Generate unique room name
    room_name = f"room-{uuid.uuid4().hex[:12]}"
    
    # 1. Create room in LiveKit via server SDK wrapper
    livekit = get_livekit()
    try:
        await livekit.create_room(room_name)
    except Exception as e:
        logger.error("livekit_create_room_failed", error=str(e), room=room_name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize video room"
        )

    # 2. Save session in DB
    session = repositories.create_session(db, title=title, room_name=room_name, agent_id=agent_id)
    logger.info("session_created", session_id=session.id, room=room_name, agent_id=agent_id)    
    # Increment metric
    try:
        from app.modules.metrics.services import TOTAL_SESSIONS
        TOTAL_SESSIONS.inc()
    except Exception:
        pass
        
    return session


def get_join_link(session) -> str:
    """Generate the frontend join URL for the customer using the session token."""
    # Assuming frontend is hosted on the same domain or known origin
    # In a real app, you might use a settings.FRONTEND_URL config
    return f"/join/{session.join_token}"


async def end_session(db: DbSession, session_id: int, agent_id: int):
    """End a session and delete the LiveKit room."""
    from datetime import datetime, timezone
    from app.modules.websocket.manager import manager
    
    session = repositories.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session.agent_id != agent_id:
        raise HTTPException(status_code=403, detail="Not authorized to end this session")
        
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Session is already completed")
        
    session.status = "completed"
    session.ended_at = datetime.now(timezone.utc)
    db.commit()
    
    # Notify all connected clients that the session has ended
    await manager.broadcast(session_id, {
        "type": "session_ended",
        "content": "This session has been ended by the agent.",
    })
    
    # Try to clean up LiveKit room
    livekit = get_livekit()
    try:
        await livekit.delete_room(session.room_name)
    except Exception as e:
        logger.warning("livekit_delete_room_failed", error=str(e), room=session.room_name)
        
    # Automatically stop any active recordings so celery tasks launch and DB updates
    try:
        from app.modules.recordings import repositories as rec_repos
        from app.modules.recordings.services import stop_recording
        active_recordings = rec_repos.list_by_session(db, session_id)
        for rec in active_recordings:
            if rec.status == "recording": # Using string literal or enum value check
                # Call stop_recording which stops egress and starts the celery task
                try:
                    await stop_recording(db, livekit, rec.id, agent_id)
                except Exception as e:
                    logger.warning("auto_stop_recording_failed", error=str(e), recording_id=rec.id)
    except Exception as e:
        logger.error("failed_to_auto_stop_recordings", error=str(e))
        
    logger.info("session_ended", session_id=session.id, agent_id=agent_id)
    return session

def create_session_archive(db: DbSession, session_id: int):
    import io
    import os
    import zipfile
    from app.modules.chat import repositories as chat_repos
    from app.modules.uploads.services import UPLOAD_DIR
    
    session = repositories.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    messages = chat_repos.list_by_session(db, session_id, limit=10000)
    
    # Create in-memory zip file
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Generate chat.txt
        chat_lines = []
        chat_lines.append(f"Chat History for Session: {session.title} (ID: {session.id})")
        chat_lines.append(f"Status: {session.status}")
        chat_lines.append("-" * 40)
        
        for msg in messages:
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            sender_name = msg.sender.email if msg.sender else "Customer"
            if msg.message_type == "file":
                chat_lines.append(f"[{timestamp}] {sender_name}: [Shared File: {msg.content}]")
            else:
                chat_lines.append(f"[{timestamp}] {sender_name}: {msg.content}")
                
        zf.writestr('chat.txt', "\n".join(chat_lines))
        
        # Bundle media files
        session_upload_dir = os.path.join(UPLOAD_DIR, str(session_id))
        if os.path.exists(session_upload_dir):
            for root, dirs, files in os.walk(session_upload_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Store them inside an 'uploads' folder in the zip
                    arcname = os.path.join('uploads', file)
                    zf.write(file_path, arcname)

        # Bundle recording video file
        from app.modules.recordings import repositories as recording_repos
        recordings = recording_repos.list_by_session(db, session_id)
        for idx, rec in enumerate(recordings):
            if rec.status == "ready" and rec.file_path:
                video_path = os.path.join(os.getcwd(), rec.file_path)
                if os.path.exists(video_path):
                    # Save video into 'recordings' folder in the zip
                    ext = os.path.splitext(rec.file_path)[1]
                    arcname = f"recordings/recording_{idx+1}{ext}"
                    zf.write(video_path, arcname)
                    
    memory_file.seek(0)
    return memory_file, f"session_{session_id}_archive.zip"
