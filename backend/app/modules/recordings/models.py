import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class RecordingStatus(str, enum.Enum):
    """Recordingstatus model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    recording = "recording"
    processing = "processing"
    ready = "ready"
    failed = "failed"

class Recording(Base):
    """Recording model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    status = Column(String, default=RecordingStatus.recording, nullable=False)
    file_path = Column(String, nullable=True)
    livekit_egress_id = Column(String, nullable=True, unique=True)
    file_size = Column(Integer, nullable=True)
    
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    session = relationship("app.modules.sessions.models.Session")
