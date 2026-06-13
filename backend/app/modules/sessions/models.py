"""
Session models for representing video call rooms.
"""
import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class SessionStatus(str, enum.Enum):
    """Status of a video session."""
    waiting = "waiting"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class Session(Base):
    """Video session database model."""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    # Unique join token for customers to enter
    join_token = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    # The LiveKit room name
    room_name = Column(String, unique=True, nullable=False)
    status = Column(String, default=SessionStatus.waiting, nullable=False)
    
    # Creator of the session (Agent)
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    agent = relationship("app.modules.auth.models.User", backref="created_sessions")
    participants = relationship("Participant", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session {self.id} ({self.status})>"
