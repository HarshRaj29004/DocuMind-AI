from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.chunking import chunk_text
from app.core.file_extraction import extract_file_text
from app.dependencies import drive_folder_id, drive_store, get_current_user, store
from app.schemas.ingestion import IngestRequest, IngestResponse

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/text", response_model=IngestResponse)
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


@router.post("/file", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
) -> IngestResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="File is empty.")

    try:
        text = extract_file_text(raw, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file has no readable content.")

    try:
        file_id = drive_store.upload_file(
            file_content=raw,
            filename=file.filename,
            folder_id=drive_folder_id,
            mimetype=_get_mimetype(file.filename),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to Google Drive: {str(exc)}",
        ) from exc

    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No valid chunks generated from file content.")

    added = store.add_chunks(
        chunks=chunks,
        source=f"{file.filename} (Drive ID: {file_id})",
        user_id=current_user["id"],
    )
    total = store.stats(user_id=current_user["id"])["chunks"]
    return IngestResponse(
        message=f"File '{file.filename}' extracted, uploaded to Google Drive (ID: {file_id}), and ingested successfully.",
        chunks_added=added,
        total_chunks=total,
    )


def _get_mimetype(filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        return "application/pdf"
    if filename.lower().endswith(".txt"):
        return "text/plain"
    return "application/octet-stream"
