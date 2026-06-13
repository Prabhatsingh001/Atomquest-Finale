import os
import shutil
import uuid

from fastapi import HTTPException, UploadFile, status

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAX_SIZE = 20 * 1024 * 1024  # 20MB
UPLOAD_DIR = "uploads"

def validate_file(file: UploadFile):
    """Execute validate file operation.
    
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
    
        Returns:
            Result of the operation.
    """
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension. Allowed: {ALLOWED_EXTENSIONS}"
        )
    
    # Fast size check by reading to end and resetting
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 20MB limit."
        )

def save_file(file: UploadFile, session_id: int) -> str:
    """Execute save file operation.
    
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
    
        Returns:
            Result of the operation.
    """
    validate_file(file)
    
    session_dir = os.path.join(UPLOAD_DIR, str(session_id))
    os.makedirs(session_dir, exist_ok=True)
    
    safe_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(session_dir, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return f"/api/uploads/download/{session_id}/{safe_filename}"
