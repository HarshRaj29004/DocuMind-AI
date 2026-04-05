from __future__ import annotations

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.chat_windows import router as chat_windows_router
from app.routes.ingestion import router as ingestion_router

app = FastAPI(title="RAG Backend", version="0.1.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(ingestion_router)
app.include_router(chat_router)
app.include_router(chat_windows_router)


if __name__ == "__main__":
	uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
