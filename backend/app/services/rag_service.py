from app.services.embedding_service import embed_query, embed_texts
from app.services.qdrant_service import (
    DOCUMENTS_COLLECTION,
    get_qdrant_client,
    search_vectors,
    upsert_vectors,
)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]


def ingest_text(
    text: str,
    doc_id: str,
    filename: str,
    user_id: str,
    workspace_id: str,
) -> int:
    chunks = chunk_text(text)
    if not chunks:
        return 0

    vectors = embed_texts(chunks)
    payloads = [
        {
            "doc_id": doc_id,
            "filename": filename,
            "chunk_index": i,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "text": chunk,
        }
        for i, chunk in enumerate(chunks)
    ]

    client = get_qdrant_client()
    upsert_vectors(client, DOCUMENTS_COLLECTION, vectors, payloads)
    return len(chunks)


def retrieve_context(
    query: str,
    user_id: str,
    workspace_id: str,
    top_k: int = 5,
) -> list[str]:
    query_vector = embed_query(query)
    client = get_qdrant_client()
    results = search_vectors(
        client,
        DOCUMENTS_COLLECTION,
        query_vector,
        top_k=top_k,
        filters={"workspace_id": workspace_id},
    )
    return [r["text"] for r in results if r.get("text")]
