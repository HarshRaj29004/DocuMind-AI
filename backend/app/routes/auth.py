from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import create_access_token, hash_password, verify_password
from app.dependencies import (
    append_chat_window_cache,
    chat_window_store,
    get_current_user,
    prime_chat_window_cache,
    user_store,
)
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest) -> TokenResponse:
    existing = user_store.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = user_store.create_user(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    created_window = chat_window_store.create_window(user_id=user["id"], title="Chat 1")
    cache_payload = append_chat_window_cache(user["id"], created_window)

    access_token = create_access_token(subject=user["email"])
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(id=user["id"], name=user.get("name"), email=user["email"]),
        chat_window_ids=cache_payload["chat_window_ids"],
        chat_windows=cache_payload["chat_windows"],
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    user = user_store.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(subject=user["email"])
    cache_payload = prime_chat_window_cache(user["id"])
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(id=user["id"], name=user.get("name"), email=user["email"]),
        chat_window_ids=cache_payload["chat_window_ids"],
        chat_windows=cache_payload["chat_windows"],
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user["id"],
        name=current_user.get("name"),
        email=current_user["email"],
    )
