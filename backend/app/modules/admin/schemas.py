
from pydantic import BaseModel


class AdminMetricsResponse(BaseModel):
    """Response model for admin system metrics."""

    active_sessions: int
    total_sessions: int
    active_participants: int
    websocket_connections: int


class ForceEndRequest(BaseModel):
    """Request model for force ending a session."""

    session_id: int
