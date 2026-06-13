from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileResponse(BaseModel):
    """Fileresponse model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    id: int
    session_id: int
    uploaded_by: int
    file_name: str
    file_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
