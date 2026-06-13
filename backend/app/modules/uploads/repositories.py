from typing import List, Optional

from sqlalchemy.orm import Session

from .models import File


def create(db: Session, session_id: int, uploaded_by: int, file_name: str, file_url: str) -> File:
    """Create a new .
    
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
    
        Returns:
            The newly created  instance.
    """
    db_file = File(
        session_id=session_id,
        uploaded_by=uploaded_by,
        file_name=file_name,
        file_url=file_url
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_by_id(db: Session, file_id: int) -> Optional[File]:
    """Retrieve by id details.
    
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
    
        Returns:
            The requested by id data.
    """
    return db.query(File).filter(File.id == file_id).first()

def list_by_session(db: Session, session_id: int) -> List[File]:
    """Execute list by session operation.
    
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
    
        Returns:
            Result of the operation.
    """
    return db.query(File).filter(File.session_id == session_id).all()
