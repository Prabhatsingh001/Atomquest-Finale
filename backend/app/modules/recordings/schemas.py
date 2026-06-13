from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from .models import RecordingStatus


class StartRecordingRequest(BaseModel):
    """Startrecordingrequest model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    session_id: int

class StopRecordingRequest(BaseModel):
    """Stoprecordingrequest model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    recording_id: int

class RecordingResponse(BaseModel):
    """Recordingresponse model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    id: int
    session_id: int
    status: RecordingStatus
    file_path: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
