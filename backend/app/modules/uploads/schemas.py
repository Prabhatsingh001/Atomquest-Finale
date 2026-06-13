from pydantic import BaseModel, ConfigDict
from datetime import datetime

class FileResponse(BaseModel):
    id: int
    session_id: int
    uploaded_by: int
    file_name: str
    file_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
