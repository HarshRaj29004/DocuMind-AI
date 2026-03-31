from __future__ import annotations

from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    id: str
    source: str
    score: float
    text: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(default=4, ge=1, le=10)


class ChatResponse(BaseModel):
    answer: str
    citations: list[SourceCitation]
