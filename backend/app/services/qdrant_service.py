import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.models import Distance, VectorParams

from app.config import get_settings

settings = get_settings()

DOCUMENTS_COLLECTION = "documents"
MEMORIES_COLLECTION = "memories"


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
        timeout=30,
    )


def ensure_collections(client: QdrantClient) -> None:
    existing = {c.name for c in client.get_collections().collections}

    for collection_name in (DOCUMENTS_COLLECTION, MEMORIES_COLLECTION):
        if collection_name not in existing:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )


def upsert_vectors(
    client: QdrantClient,
    collection: str,
    vectors: list[list[float]],
    payloads: list[dict[str, Any]],
    ids: list[str] | None = None,
) -> None:
    if ids is None:
        ids = [str(uuid.uuid4()) for _ in vectors]

    points = [
        qdrant_models.PointStruct(id=pid, vector=vec, payload=payload)
        for pid, vec, payload in zip(ids, vectors, payloads)
    ]
    client.upsert(collection_name=collection, points=points)


def search_vectors(
    client: QdrantClient,
    collection: str,
    query_vector: list[float],
    top_k: int = 5,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    qdrant_filter = None
    if filters:
        must_conditions = [
            qdrant_models.FieldCondition(
                key=key,
                match=qdrant_models.MatchValue(value=value),
            )
            for key, value in filters.items()
        ]
        qdrant_filter = qdrant_models.Filter(must=must_conditions)

    results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=top_k,
        query_filter=qdrant_filter,
        with_payload=True,
    )
    return [{"score": r.score, **r.payload} for r in results]


def delete_vectors_by_filter(
    client: QdrantClient, collection: str, filters: dict[str, Any]
) -> None:
    must_conditions = [
        qdrant_models.FieldCondition(key=key, match=qdrant_models.MatchValue(value=value))
        for key, value in filters.items()
    ]
    client.delete(
        collection_name=collection,
        points_selector=qdrant_models.FilterSelector(
            filter=qdrant_models.Filter(must=must_conditions)
        ),
    )
