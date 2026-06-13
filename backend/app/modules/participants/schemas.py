"""
Schemas for Participant joining.
"""
from pydantic import BaseModel


class JoinRequest(BaseModel):
    """Payload provided by a customer entering a join token."""
    name: str


class JoinResponse(BaseModel):
    """Response containing LiveKit token and room info."""
    livekit_token: str
    room_name: str
    identity: str
    session_id: int
    backend_token: str | None = None
    user_id: int | None = None
