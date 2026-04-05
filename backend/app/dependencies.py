from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.db.chat_window import ChatWindowStore
from app.db.google_drive_store import GoogleDriveStore
from app.db.user_store import SupabaseUserStore
from app.db.vector_store import InMemoryVectorStore

# Load backend/.env independent of working directory.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

store = InMemoryVectorStore()
user_store = SupabaseUserStore()
chat_window_store = ChatWindowStore()
drive_store = GoogleDriveStore()
drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# In-memory cache for quick chat window reads after login.
_chat_window_cache: dict[int, dict] = {}


def _serialize_chat_cache_payload(windows: list[dict]) -> dict:
    return {
        "chat_window_ids": [int(item["id"]) for item in windows],
        "chat_windows": windows,
    }


def get_chat_window_cache(user_id: int) -> dict | None:
    return _chat_window_cache.get(user_id)


def prime_chat_window_cache(user_id: int) -> dict:
    cached = get_chat_window_cache(user_id)
    if cached is not None:
        return cached

    windows = chat_window_store.list_windows(user_id)
    payload = _serialize_chat_cache_payload(windows)
    _chat_window_cache[user_id] = payload
    return payload


def refresh_chat_window_cache(user_id: int) -> dict:
    windows = chat_window_store.list_windows(user_id)
    payload = _serialize_chat_cache_payload(windows)
    _chat_window_cache[user_id] = payload
    return payload


def append_chat_window_cache(user_id: int, window: dict) -> dict:
    payload = _chat_window_cache.get(user_id) or {
        "chat_window_ids": [],
        "chat_windows": [],
    }
    payload["chat_window_ids"].append(int(window["id"]))
    payload["chat_windows"].append(window)
    _chat_window_cache[user_id] = payload
    return payload


def remove_chat_window_cache(user_id: int, window_id: int) -> dict:
    payload = _chat_window_cache.get(user_id) or {
        "chat_window_ids": [],
        "chat_windows": [],
    }
    payload["chat_window_ids"] = [cid for cid in payload["chat_window_ids"] if cid != window_id]
    payload["chat_windows"] = [item for item in payload["chat_windows"] if int(item["id"]) != window_id]
    _chat_window_cache[user_id] = payload
    return payload


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_access_token(token)
        user_email = payload.get("sub")
        if not user_email:
            raise ValueError("Missing user subject")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token") from exc

    user = user_store.get_user_by_email(user_email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
