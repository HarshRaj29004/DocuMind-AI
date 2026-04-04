from __future__ import annotations
import uvicorn
from dotenv import load_dotenv

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.core.chunking import chunk_text
from app.core.rag_pipeline import generate_answer
from app.core.retrieval import retrieve_context
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.db.user_store import SupabaseUserStore
from app.db.vector_store import InMemoryVectorStore
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.schemas.chat import ChatRequest, ChatResponse, SourceCitation
from app.schemas.ingestion import IngestRequest, IngestResponse

load_dotenv()

app = FastAPI(title="RAG Backend", version="0.1.0")
store = InMemoryVectorStore()
user_store = SupabaseUserStore()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
	return {"status": "ok", "store": store.stats()}


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
	try:
		payload = decode_access_token(token)
		user_email = payload.get("sub")
		if not user_email:
			raise ValueError("Missing user subject")
	except ValueError as exc:
		raise HTTPException(status_code=401, detail="Invalid authentication token") from exc

	user = user_store.get_user_by_email(user_email)
	if not user:
		raise HTTPException(status_code=401, detail="User not found")

	return user


@app.post("/auth/register", response_model=TokenResponse)
def register(payload: RegisterRequest) -> TokenResponse:
	existing = user_store.get_user_by_email(payload.email)
	if existing:
		raise HTTPException(status_code=409, detail="Email already registered")

	user = user_store.create_user(
		name=payload.name,
		email=payload.email,
		password_hash=hash_password(payload.password),
	)
	access_token = create_access_token(subject=user["email"])
	return TokenResponse(
		access_token=access_token,
		user=UserResponse(id=user["id"], name=user.get("name"), email=user["email"]),
	)


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
	user = user_store.get_user_by_email(payload.email)
	if not user or not verify_password(payload.password, user["password_hash"]):
		raise HTTPException(status_code=401, detail="Invalid email or password")

	access_token = create_access_token(subject=user["email"])
	return TokenResponse(
		access_token=access_token,
		user=UserResponse(id=user["id"], name=user.get("name"), email=user["email"]),
	)


@app.get("/auth/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
	return UserResponse(
		id=current_user["id"],
		name=current_user.get("name"),
		email=current_user["email"],
	)


@app.post("/ingest/text", response_model=IngestResponse)
def ingest_text(
	payload: IngestRequest,
	current_user: dict = Depends(get_current_user),
) -> IngestResponse:
	chunks = chunk_text(payload.text)
	if not chunks:
		raise HTTPException(status_code=400, detail="No valid content found to ingest.")

	added = store.add_chunks(chunks=chunks, source=payload.source_name, user_id=current_user["id"])
	total = store.stats(user_id=current_user["id"])["chunks"]
	return IngestResponse(
		message="Text ingested successfully.",
		chunks_added=added,
		total_chunks=total,
	)


@app.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(
	file: UploadFile = File(...),
	current_user: dict = Depends(get_current_user),
) -> IngestResponse:
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

	added = store.add_chunks(chunks=chunks, source=file.filename, user_id=current_user["id"])
	total = store.stats(user_id=current_user["id"])["chunks"]
	return IngestResponse(
		message=f"File '{file.filename}' ingested successfully.",
		chunks_added=added,
		total_chunks=total,
	)


@app.post("/chat", response_model=ChatResponse)
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


if __name__ == "__main__":
	uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
