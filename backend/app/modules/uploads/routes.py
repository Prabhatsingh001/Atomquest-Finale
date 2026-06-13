import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.permissions import get_current_user
from app.modules.auth.models import User
from app.modules.sessions import repositories as session_repos
from app.modules.chat import services as chat_services
from app.modules.websocket.manager import manager
from . import schemas, services, repositories

router = APIRouter(prefix="/uploads", tags=["Uploads"])

@router.post("", response_model=schemas.FileResponse)
async def upload_file(
    session_id: int = Form(...),
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a file to a session."""
    session = session_repos.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is not active")

    # Save physical file
    file_url = services.save_file(file, session_id)
    
    # Save file record
    db_file = repositories.create(db, session_id, current_user.id, file.filename, file_url)
    
    # Create chat message for the file
    content = f"[{file.filename}]({file_url})"
    message = chat_services.send_message(
        db=db,
        session_id=session_id,
        sender_id=current_user.id,
        content=content,
        message_type="file"
    )
    
    # Broadcast message via websocket
    await manager.broadcast(session_id, {
        "type": "chat",
        "message": message.model_dump(mode="json")
    })
    
    return db_file

@router.get("/download/{session_id}/{filename}")
def download_file(session_id: int, filename: str):
    """Serve uploaded files."""
    file_path = os.path.join(services.UPLOAD_DIR, str(session_id), filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FastAPIFileResponse(file_path)

@router.get("/session/{session_id}", response_model=list[schemas.FileResponse])
def get_session_files(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all files in a session."""
    return repositories.list_by_session(db, session_id)
