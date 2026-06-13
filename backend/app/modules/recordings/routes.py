from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.livekit import LiveKitService, get_livekit
from app.core.permissions import get_current_user
from app.db.database import get_db
from app.modules.auth.models import User

from . import repositories, schemas, services

router = APIRouter(prefix="/recordings", tags=["Recordings"])


@router.post("/start", response_model=schemas.RecordingResponse)
async def start_recording(
    req: schemas.StartRecordingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    livekit: LiveKitService = Depends(get_livekit),
):
    """Start a recording for a session.

    Args:
        req (schemas.StartRecordingRequest): Request payload containing the session ID.
        db (Session): Database session dependency.
        current_user (User): Authenticated user dependency.
        livekit (LiveKitService): LiveKit service dependency.

    Returns:
        schemas.RecordingResponse: The newly created recording object.

    Raises:
        HTTPException: If the user is not an agent or the session is invalid.
    """
    if current_user.role != "agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents can start recordings",
        )

    recording = await services.start_recording(
        db, livekit, req.session_id, current_user.id
    )
    return recording


@router.post("/stop", response_model=schemas.RecordingResponse)
async def stop_recording(
    req: schemas.StopRecordingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    livekit: LiveKitService = Depends(get_livekit),
):
    """Stop an active recording.

    Args:
        req (schemas.StopRecordingRequest): Request payload containing the recording ID.
        db (Session): Database session dependency.
        current_user (User): Authenticated user dependency.
        livekit (LiveKitService): LiveKit service dependency.

    Returns:
        schemas.RecordingResponse: The updated recording object.

    Raises:
        HTTPException: If the user is not an agent or the recording is invalid.
    """
    if current_user.role != "agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents can stop recordings",
        )

    recording = await services.stop_recording(
        db, livekit, req.recording_id, current_user.id
    )
    return recording


@router.get("/session/{session_id}", response_model=List[schemas.RecordingResponse])
def get_session_recordings(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all recordings for a session."""
    if current_user.role != "agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    recordings = repositories.list_by_session(db, session_id)
    return recordings


@router.get("/{recording_id}", response_model=schemas.RecordingResponse)
def get_recording(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recording details."""
    if current_user.role != "agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    recording = repositories.get_by_id(db, recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found"
        )

    return recording
