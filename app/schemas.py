from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
import re


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', v):
            raise ValueError('Username must be 3-20 characters, alphanumeric and underscore only')
        return v


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = dict(from_attributes=True)


class UserResponse(UserInDB):
    pass


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    username: str
    password: str
