from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import (
    append_chat_window_cache,
    chat_window_store,
    get_current_user,
    prime_chat_window_cache,
    remove_chat_window_cache,
)
from app.schemas.chat_window import (
    ChatWindowCreateRequest,
    ChatWindowListResponse,
    ChatWindowResponse,
)

router = APIRouter(prefix="/chat-windows", tags=["chat-windows"])


@router.get("", response_model=ChatWindowListResponse)
def list_chat_windows(current_user: dict = Depends(get_current_user)) -> ChatWindowListResponse:
    payload = prime_chat_window_cache(current_user["id"])
    return ChatWindowListResponse(
        chat_window_ids=payload["chat_window_ids"],
        chat_windows=payload["chat_windows"],
    )


@router.post("", response_model=ChatWindowResponse)
def create_chat_window(
    payload: ChatWindowCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> ChatWindowResponse:
    created = chat_window_store.create_window(user_id=current_user["id"], title=payload.title)
    append_chat_window_cache(current_user["id"], created)
    return ChatWindowResponse(**created)


@router.delete("/{window_id}", response_model=ChatWindowListResponse)
def delete_chat_window(
    window_id: int,
    current_user: dict = Depends(get_current_user),
) -> ChatWindowListResponse:
    deleted = chat_window_store.delete_window(user_id=current_user["id"], window_id=window_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat window not found")

    payload = remove_chat_window_cache(current_user["id"], window_id)
    return ChatWindowListResponse(
        chat_window_ids=payload["chat_window_ids"],
        chat_windows=payload["chat_windows"],
    )
