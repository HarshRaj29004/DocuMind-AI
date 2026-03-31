from __future__ import annotations


def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    """Simple local answer synthesis from retrieved chunks."""
    if not retrieved_chunks:
        return "I could not find relevant context in the ingested data yet. Upload or ingest more content and try again."

    top_chunks = retrieved_chunks[:3]
    context_lines = [f"- {item['text']}" for item in top_chunks]
    context_block = "\n".join(context_lines)

    return (
        f"Question: {query}\n\n"
        "Based on the indexed documents, here are the most relevant excerpts:\n"
        f"{context_block}\n\n"
        "You can use these citations for grounded follow-up questions."
    )
