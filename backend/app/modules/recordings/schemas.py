from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from .models import RecordingStatus

class StartRecordingRequest(BaseModel):
    session_id: int

class StopRecordingRequest(BaseModel):
    recording_id: int

class RecordingResponse(BaseModel):
    id: int
    session_id: int
    status: RecordingStatus
    file_path: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
