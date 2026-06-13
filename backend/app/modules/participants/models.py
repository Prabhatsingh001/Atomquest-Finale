"""
Participant models representing users in a session.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base


class Participant(Base):
    """Participant in a video session."""
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    # If a registered user, this is set. If ephemeral customer, might be null or point to an ephemeral user row.
    # We will point it to the users table since we create ephemeral users.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # LiveKit participant identity
    identity = Column(String, unique=True, nullable=False)
    # Display name in the room
    name = Column(String, nullable=False)
    
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    left_at = Column(DateTime, nullable=True)
    
    # Track if they are currently connected
    is_connected = Column(Boolean, default=False)

    # Relationships
    session = relationship("app.modules.sessions.models.Session", back_populates="participants")
    user = relationship("app.modules.auth.models.User", backref="session_participations")

    def __repr__(self):
        return f"<Participant {self.identity} (Session {self.session_id})>"
