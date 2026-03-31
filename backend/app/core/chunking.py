from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks for retrieval."""
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 4)

    chunks: list[str] = []
    start = 0
    step = max(1, chunk_size - overlap)

    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(cleaned):
            break
        start += step

    return chunks
