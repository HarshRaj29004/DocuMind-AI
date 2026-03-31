from __future__ import annotations

from app.db.vector_store import InMemoryVectorStore


def retrieve_context(query: str, store: InMemoryVectorStore, top_k: int = 4) -> list[dict]:
    return store.query(query_text=query, top_k=top_k)
