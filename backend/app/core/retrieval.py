from __future__ import annotations

from app.db.vector_store import InMemoryVectorStore


def retrieve_context(
    query: str,
    store: InMemoryVectorStore,
    user_id: int,
    top_k: int = 4,
) -> list[dict]:
    return store.query(query_text=query, user_id=user_id, top_k=top_k)
