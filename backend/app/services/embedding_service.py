from functools import lru_cache

from fastembed import TextEmbedding

from app.config import get_settings

settings = get_settings()

# fastembed model that matches 384-dim Qdrant collection config.
# "BAAI/bge-small-en-v1.5" produces 384-dim embeddings using ONNX (no torch required).
_FASTEMBED_MODEL = "BAAI/bge-small-en-v1.5"


@lru_cache(maxsize=1)
def _get_model() -> TextEmbedding:
    return TextEmbedding(model_name=_FASTEMBED_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return [emb.tolist() for emb in model.embed(texts)]


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
