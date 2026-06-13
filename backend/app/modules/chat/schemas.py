from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    """Messagecreate model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    content: str
    message_type: str = "text"

class MessageResponse(BaseModel):
    """Messageresponse model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    id: int
    session_id: int
    sender_id: int | None = None
    sender_name: str | None = None
    sender_role: str | None = None
    content: str
    message_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
