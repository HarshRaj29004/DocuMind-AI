from __future__ import annotations

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    text: str = Field(..., min_length=10)
    source_name: str = Field(default="manual-input")


class IngestResponse(BaseModel):
    message: str
    chunks_added: int
    total_chunks: int
