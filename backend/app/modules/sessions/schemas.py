"""
Schemas for Session management.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.modules.sessions.models import SessionStatus


class SessionCreate(BaseModel):
    """Sessioncreate model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    title: str

class ParticipantResponse(BaseModel):
    """Participantresponse model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    id: int
    user_id: int
    identity: str
    name: str
    joined_at: datetime
    left_at: Optional[datetime] = None
    is_connected: bool
    model_config = ConfigDict(from_attributes=True)

class SessionResponse(BaseModel):
    """Sessionresponse model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    id: int
    title: str
    join_token: str
    room_name: str
    status: SessionStatus
    agent_id: int
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class SessionDetailResponse(SessionResponse):
    """Sessiondetailresponse model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    participants: List[ParticipantResponse] = []
    message_count: int = 0
    duration_seconds: Optional[int] = 0


class SessionJoinLinkResponse(BaseModel):
    """Sessionjoinlinkresponse model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    join_url: str
    token: str
