from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.rag_pipeline import generate_answer
from app.core.retrieval import retrieve_context
from app.dependencies import get_current_user, store
from app.schemas.chat import ChatRequest, ChatResponse, SourceCitation

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: dict = Depends(get_current_user),
) -> ChatResponse:
    retrieved = retrieve_context(
        query=payload.query,
        store=store,
        user_id=current_user["id"],
        top_k=payload.top_k,
    )
    answer = generate_answer(query=payload.query, retrieved_chunks=retrieved)
    citations = [SourceCitation(**item) for item in retrieved]
    return ChatResponse(answer=answer, citations=citations)
