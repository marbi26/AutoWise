from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    saved_vehicles_count: int = 0
    recommendations_count: int = 0
    created_at: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse
