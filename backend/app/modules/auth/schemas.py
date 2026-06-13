"""
Pydantic schemas for auth API.
"""
from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    """Loginrequest model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    """Signuprequest model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Userresponse model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    id: int
    name: str | None = None
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    """Loginresponse model or schema representation.
    
        Attributes:
            None specified explicitly.
    """
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
