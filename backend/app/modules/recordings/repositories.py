from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from .models import Recording, RecordingStatus

def create(db: Session, session_id: int, egress_id: str) -> Recording:
    db_recording = Recording(
        session_id=session_id,
        livekit_egress_id=egress_id,
        status=RecordingStatus.recording
    )
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording

def update_status(db: Session, recording_id: int, status: RecordingStatus, file_path: Optional[str] = None) -> Optional[Recording]:
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
    return db.query(Recording).filter(Recording.session_id == session_id).all()

def get_by_id(db: Session, recording_id: int) -> Optional[Recording]:
    return db.query(Recording).filter(Recording.id == recording_id).first()
