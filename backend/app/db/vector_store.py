from __future__ import annotations

import os
from dotenv import load_dotenv
from threading import Lock
from uuid import uuid4

from pinecone import Pinecone, ServerlessSpec

load_dotenv()

class InMemoryVectorStore:
    def __init__(self) -> None:
        api_key = os.getenv("PINECONE_API_KEY","")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY is required to use Pinecone vector storage.")

        self._index_name = os.getenv("PINECONE_INDEX_NAME")
        self._embedding_model = os.getenv("PINECONE_EMBEDDING_MODEL")
        self._host = os.getenv("")

        self._pc = Pinecone(api_key=api_key)
        existing_indexes = self._get_existing_index_names()
        # if self._index_name not in existing_indexes:
        #     self._pc.create_index(
        #         name=self._index_name,
        #         metric="cosine",
        #         dimension=1024,
        #     )

        self._index = self._pc.Index(self._index_name)
        self._lock = Lock()
        self._user_chunk_counts: dict[int, int] = {}

    def _get_existing_index_names(self) -> set[str]:
        indexes = self._pc.list_indexes()
        if hasattr(indexes, "names"):
            return set(indexes.names())
        if isinstance(indexes, list):
            return {item.get("name") for item in indexes if isinstance(item, dict) and item.get("name")}
        if isinstance(indexes, dict):
            values = indexes.get("indexes", [])
            return {item.get("name") for item in values if isinstance(item, dict) and item.get("name")}
        return set()

    @staticmethod
    def _as_dict(response: object) -> dict:
        if isinstance(response, dict):
            return response
        if hasattr(response, "to_dict"):
            return response.to_dict()
        return {}

    def _get_embedding(self, text: str) -> list[float]:
        response = self._pc.inference.embed(
            model=self._embedding_model,
            inputs=[text],
            parameters={"input_type": "passage"},
        )
        return response[0]["values"] if response and response[0] else []

    def add_chunks(self, chunks: list[str], source: str, user_id: int) -> int:
        vectors: list[dict] = []
        with self._lock:
            for offset, chunk in enumerate(chunks):
                embedding = self._get_embedding(chunk)
                if not embedding:
                    continue

                vectors.append(
                    {
                        "id": f"u{user_id}-{uuid4().hex[:8]}-{offset}",
                        "values": embedding,
                        "metadata": {
                            "user_id": user_id,
                            "text": chunk,
                            "source": source,
                        },
                    }
                )

        if vectors:
            self._index.upsert(vectors=vectors)
            with self._lock:
                self._user_chunk_counts[user_id] = self._user_chunk_counts.get(user_id, 0) + len(vectors)
        return len(vectors)

    def query(self, query_text: str, user_id: int, top_k: int = 4) -> list[dict]:
        query_embedding = self._get_embedding(query_text)
        if not query_embedding:
            return []

        response = self._index.query(
            vector=query_embedding,
            top_k=top_k,
            filter={"user_id": {"$eq": user_id}},
            include_metadata=True,
        )
        response_dict = self._as_dict(response)

        results = []
        for match in response_dict.get("matches", []):
            metadata = match.get("metadata", {})
            results.append(
                {
                    "id": match.get("id", ""),
                    "text": metadata.get("text", ""),
                    "source": metadata.get("source", ""),
                    "score": round(float(match.get("score", 0.0)), 4),
                }
            )
        return results

    def stats(self, user_id: int | None = None) -> dict[str, int]:
        if user_id is not None:
            with self._lock:
                return {"chunks": int(self._user_chunk_counts.get(user_id, 0))}

        info = self._index.describe_index_stats()
        info_dict = self._as_dict(info)
        return {"chunks": int(info_dict.get("total_vector_count", 0))}
