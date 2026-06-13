from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from .models import Recording, RecordingStatus


def create(db: Session, session_id: int, egress_id: str) -> Recording:
    """Create a new recording record with 'recording' status.

    Args:
        db (Session): Database session.
        session_id (int): The associated session ID.
        egress_id (str): The LiveKit egress process ID.

    Returns:
        Recording: The created database recording object.
    """
    db_recording = Recording(
        session_id=session_id,
        livekit_egress_id=egress_id,
        status=RecordingStatus.recording,
    )
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording


def update_status(
    db: Session,
    recording_id: int,
    status: RecordingStatus,
    file_path: Optional[str] = None,
) -> Optional[Recording]:
    """Update the status of an existing recording and optionally set its file path.

    Args:
        db (Session): Database session.
        recording_id (int): The ID of the recording to update.
        status (RecordingStatus): The new status to apply.
        file_path (Optional[str], optional): The path to the completed file. Defaults to None.

    Returns:
        Optional[Recording]: The updated recording object if found, otherwise None.
    """
    db_recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not db_recording:
        return None
    db_recording.status = status
    if file_path:
        db_recording.file_path = file_path
    if status in [RecordingStatus.ready, RecordingStatus.failed]:
        db_recording.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_recording)
    return db_recording


def list_by_session(db: Session, session_id: int) -> List[Recording]:
    """Retrieve all recordings associated with a session.

    Args:
        db (Session): Database session.
        session_id (int): The associated session ID.

    Returns:
        List[Recording]: A list of recordings for the session.
    """
    return db.query(Recording).filter(Recording.session_id == session_id).all()


def get_by_id(db: Session, recording_id: int) -> Optional[Recording]:
    """Retrieve a recording by its primary key ID.

    Args:
        db (Session): Database session.
        recording_id (int): The internal ID of the recording.

    Returns:
        Optional[Recording]: The recording if found, else None.
    """
    return db.query(Recording).filter(Recording.id == recording_id).first()
