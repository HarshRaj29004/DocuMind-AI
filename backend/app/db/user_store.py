from __future__ import annotations

import os
from dotenv import load_dotenv

from supabase import Client, create_client

load_dotenv()

class SupabaseUserStore:
    def __init__(self) -> None:
        supabase_url = os.getenv("SUPABASE_URL","").strip()
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY","").strip()
        if not supabase_url or not supabase_key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_DEFAULT_KEY are required"
            )

        self._users_table = os.getenv("SUPABASE_USERS_TABLE", "users").strip()
        self._client: Client = create_client(supabase_url, supabase_key)

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.lower().strip()

    def create_user(self, name: str, email: str, password_hash: str) -> dict:
        normalized_email = self._normalize_email(email)
        payload = {
            "name": name.strip(),
            "email": normalized_email,
            "hashed_password": password_hash,
        }
        try:
            response = (
                self._client.table(self._users_table)
                .insert(payload)
                .execute()
            )
        except Exception as exc:
            error_text = str(exc).lower()
            if "duplicate key" in error_text or "already" in error_text or "23505" in error_text:
                raise ValueError("Email already registered") from exc
            raise

        if not response.data:
            raise RuntimeError("Supabase insert returned no user data")

        row = response.data[0]
        return {
            "id": row.get("id"),
            "name": row.get("name"),
            "email": row.get("email"),
        }

    def get_user_by_email(self, email: str) -> dict | None:
        normalized_email = self._normalize_email(email)
        response = (
            self._client.table(self._users_table)
            .select("id, name, email, hashed_password")
            .eq("email", normalized_email)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        row = response.data[0]
        return {
            "id": row.get("id"),
            "name": row.get("name"),
            "email": row.get("email"),
            "password_hash": row.get("password_hash", ""),
        }
