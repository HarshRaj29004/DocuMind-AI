from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.core.chunking import chunk_text
from app.core.rag_pipeline import generate_answer
from app.core.retrieval import retrieve_context
from app.db.vector_store import InMemoryVectorStore
from app.schemas.chat import ChatRequest, ChatResponse, SourceCitation
from app.schemas.ingestion import IngestRequest, IngestResponse

app = FastAPI(title="RAG Backend", version="0.1.0")
store = InMemoryVectorStore()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
	return {"status": "ok", "store": store.stats()}


@app.post("/ingest/text", response_model=IngestResponse)
def ingest_text(payload: IngestRequest) -> IngestResponse:
	chunks = chunk_text(payload.text)
	if not chunks:
		raise HTTPException(status_code=400, detail="No valid content found to ingest.")

	added = store.add_chunks(chunks=chunks, source=payload.source_name)
	total = store.stats()["chunks"]
	return IngestResponse(
		message="Text ingested successfully.",
		chunks_added=added,
		total_chunks=total,
	)


@app.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)) -> IngestResponse:
	if not file.filename:
		raise HTTPException(status_code=400, detail="Missing filename.")

	raw = await file.read()
	try:
		text = raw.decode("utf-8")
	except UnicodeDecodeError:
		text = raw.decode("latin-1", errors="ignore")

	chunks = chunk_text(text)
	if not chunks:
		raise HTTPException(status_code=400, detail="Uploaded file has no readable content.")

	added = store.add_chunks(chunks=chunks, source=file.filename)
	total = store.stats()["chunks"]
	return IngestResponse(
		message=f"File '{file.filename}' ingested successfully.",
		chunks_added=added,
		total_chunks=total,
	)


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
	retrieved = retrieve_context(query=payload.query, store=store, top_k=payload.top_k)
	answer = generate_answer(query=payload.query, retrieved_chunks=retrieved)
	citations = [SourceCitation(**item) for item in retrieved]
	return ChatResponse(answer=answer, citations=citations)
