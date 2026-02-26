import os
import uuid
from pathlib import Path

from app.services.rag_service import ingest_text
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def ingest_document(
    self,
    file_path: str,
    filename: str,
    workspace_id: str,
    user_id: str,
) -> dict:
    try:
        from unstructured.partition.auto import partition

        elements = partition(filename=file_path)
        full_text = "\n\n".join(str(el) for el in elements if str(el).strip())

        if not full_text:
            return {"status": "empty", "filename": filename, "chunks": 0}

        doc_id = str(uuid.uuid4())
        chunk_count = ingest_text(
            text=full_text,
            doc_id=doc_id,
            filename=filename,
            user_id=user_id,
            workspace_id=workspace_id,
        )

        # Clean up temp file after ingestion
        try:
            os.remove(file_path)
        except OSError:
            pass

        return {
            "status": "success",
            "doc_id": doc_id,
            "filename": filename,
            "chunks": chunk_count,
        }

    except Exception as exc:
        raise self.retry(exc=exc)
