"""
Schemas for Session management.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.modules.sessions.models import SessionStatus

class SessionCreate(BaseModel):
    title: str

class ParticipantResponse(BaseModel):
    id: int
    user_id: int
    identity: str
    name: str
    joined_at: datetime
    left_at: Optional[datetime] = None
    is_connected: bool
    model_config = ConfigDict(from_attributes=True)

class SessionResponse(BaseModel):
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
    participants: List[ParticipantResponse] = []
    message_count: int = 0
    duration_seconds: Optional[int] = 0


class SessionJoinLinkResponse(BaseModel):
    join_url: str
    token: str
