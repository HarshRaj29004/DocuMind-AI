from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from supabase import Client, create_client

load_dotenv()


class ChatWindowStore:
    def __init__(self) -> None:
        supabase_url = os.getenv("SUPABASE_URL", "").strip()
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        if not supabase_url or not supabase_key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required"
            )

        self._table = os.getenv("SUPABASE_CHAT_WINDOW_TABLE", "chat_window").strip()
        self._client: Client = create_client(supabase_url, supabase_key)

    @staticmethod
    def _normalize_window(row: dict) -> dict:
        return {
            "id": int(row.get("id")),
            "user_id": int(row.get("user_id")),
            "title": row.get("title") or "Chat",
            "created_at": row.get("created_at"),
        }

    def list_windows(self, user_id: int) -> list[dict]:
        response = (
            self._client.table(self._table)
            .select("id, user_id, title, created_at")
            .eq("user_id", user_id)
            .order("id", desc=False)
            .execute()
        )
        return [self._normalize_window(row) for row in (response.data or [])]

    def list_window_ids(self, user_id: int) -> list[int]:
        return [row["id"] for row in self.list_windows(user_id)]

    def create_window(self, user_id: int, title: str) -> dict:
        payload = {
            "title": title.strip(),
            "user_id": user_id,
        }
        try:
            response = (
                self._client.table(self._table)
                .insert(payload)
                .select("id, user_id, title, created_at")
                .execute()
            )
        except Exception as exc:
            raise RuntimeError("Failed to create chat window") from exc

        if not response.data:
            raise RuntimeError("Supabase insert returned no chat window data")

        row = response.data[0]
        return self._normalize_window(row)

    def delete_window(self, user_id: int, window_id: int) -> bool:
        try:
            response = (
                self._client.table(self._table)
                .delete()
                .eq("id", window_id)
                .eq("user_id", user_id)
                .select("id")
                .execute()
            )
        except Exception as exc:
            raise RuntimeError("Failed to delete chat window") from exc

        return bool(response.data)