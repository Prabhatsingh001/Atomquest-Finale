"""
Role-based access control dependencies for FastAPI.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    """FastAPI dependency that extracts and validates the JWT token,
    then returns the current user from the database.

    Args:
        credentials (HTTPAuthorizationCredentials): The authorization token from the request.
        db (Session): The database session.

    Returns:
        User: The authenticated user instance.

    Raises:
        HTTPException: If the token is invalid, revoked, missing subject, or the user is not found.
    """
    token = credentials.credentials

    from app.db.redis import redis_client

    if redis_client.get(f"blacklist:{token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )

    # Import here to avoid circular imports
    from app.modules.auth.models import User

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_role(*allowed_roles: str):
    """Factory for a FastAPI dependency that enforces role-based access.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("admin"))])

    Args:
        *allowed_roles (str): Variable length argument list of roles allowed to access the endpoint.

    Returns:
        Callable: A dependency function that verifies the user's role.
    """

    async def role_checker(current_user=Depends(get_current_user)):
        """Execute role checker operation.
        
            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.
        
            Returns:
                Result of the operation.
        """
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not authorized. Required: {allowed_roles}",
            )
        return current_user

    return role_checker
