from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterParams(BaseModel):
    username: str = Field(..., min_length=5, max_length=20)
    email: EmailStr = Field("user@tsumiki.com")
    password: str = Field(default="", min_length=8, max_length=24)


class UserInfo(BaseModel):
    username: str = Field(..., min_length=5, max_length=20)
    email: EmailStr = Field("user@tsumiki.com")
    total_space: int
    used_space: int

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    user: UserInfo
    access_token: str

    model_config = ConfigDict(from_attributes=True)


class UpdatePasswordParams(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=24)
    new_password: str = Field(..., min_length=8, max_length=24)
