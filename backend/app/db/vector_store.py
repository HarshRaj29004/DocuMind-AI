from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

from app.core.embedding import cosine_similarity, embed_text


@dataclass
class StoredChunk:
    id: str
    text: str
    source: str
    embedding: dict[str, float]


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._chunks: list[StoredChunk] = []
        self._lock = Lock()

    def add_chunks(self, chunks: list[str], source: str) -> int:
        with self._lock:
            start_index = len(self._chunks)
            for offset, chunk in enumerate(chunks):
                chunk_id = f"{source}-{start_index + offset}"
                self._chunks.append(
                    StoredChunk(
                        id=chunk_id,
                        text=chunk,
                        source=source,
                        embedding=embed_text(chunk),
                    )
                )
        return len(chunks)

    def query(self, query_text: str, top_k: int = 4) -> list[dict]:
        query_embedding = embed_text(query_text)

        scored = []
        with self._lock:
            for chunk in self._chunks:
                score = cosine_similarity(query_embedding, chunk.embedding)
                if score > 0:
                    scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)

        results = []
        for score, chunk in scored[:top_k]:
            results.append(
                {
                    "id": chunk.id,
                    "text": chunk.text,
                    "source": chunk.source,
                    "score": round(score, 4),
                }
            )
        return results

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {"chunks": len(self._chunks)}
