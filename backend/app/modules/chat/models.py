"""
Message models for real-time chat in sessions.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class MessageType(str, enum.Enum):
    """Types of chat messages."""
    text = "text"
    file = "file"
    system = "system"


class Message(Base):
    """A chat message sent within a video session."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    # The user who sent the message (could be agent or ephemeral customer)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Message type
    message_type = Column(String, default=MessageType.text, nullable=False)
    
    # Message content (for text messages) or file URL/identifier
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    session = relationship("app.modules.sessions.models.Session", backref="messages")
    sender = relationship("app.modules.auth.models.User", backref="sent_messages")

    def __repr__(self):
        """Execute repr operation.
        
            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.
        
            Returns:
                Result of the operation.
        """
        return f"<Message {self.id} (Session {self.session_id})>"
