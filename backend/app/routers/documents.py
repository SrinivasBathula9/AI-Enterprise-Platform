import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.dependencies import get_current_user, get_db
from app.workers.ingestion import ingest_document

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "text/csv",
}


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    workspace_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Supported: PDF, DOCX, TXT, MD, CSV",
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size is {settings.max_upload_size_mb}MB.",
        )

    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "upload").suffix
    temp_path = str(upload_path / f"{uuid.uuid4()}{suffix}")

    with open(temp_path, "wb") as f:
        f.write(content)

    task = ingest_document.delay(
        file_path=temp_path,
        filename=file.filename or "upload",
        workspace_id=str(workspace_id),
        user_id=current_user["user_id"],
    )

    return {"task_id": task.id, "filename": file.filename, "status": "queued"}


@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    from app.workers.celery_app import celery_app
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
