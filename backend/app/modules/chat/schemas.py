from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MessageCreate(BaseModel):
    content: str
    message_type: str = "text"

class MessageResponse(BaseModel):
    id: int
    session_id: int
    sender_id: int | None = None
    sender_name: str | None = None
    sender_role: str | None = None
    content: str
    message_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
