"""
User model for authentication and role management.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Integer, String

from app.db.database import Base


class UserRole(str, enum.Enum):
    """Roles in the AtomQuest system."""
    agent = "agent"
    customer = "customer"
    admin = "admin"


class User(Base):
    """User database model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=True), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        """Execute repr operation.
        
            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.
        
            Returns:
                Result of the operation.
        """
        return f"<User {self.email} ({self.role})>"
