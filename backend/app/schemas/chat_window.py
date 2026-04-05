from __future__ import annotations

from pydantic import BaseModel, Field


class ChatWindowCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)


class ChatWindowResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: str | None = None


class ChatWindowListResponse(BaseModel):
    chat_window_ids: list[int]
    chat_windows: list[ChatWindowResponse]
