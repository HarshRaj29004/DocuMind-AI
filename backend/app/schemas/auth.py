from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.chat_window import ChatWindowResponse


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: int
    name: str | None = None
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    chat_window_ids: list[int] = Field(default_factory=list)
    chat_windows: list[ChatWindowResponse] = Field(default_factory=list)
