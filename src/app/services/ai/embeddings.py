from app.services.ai.logging_utils import log_embedding_call
from app.services.ai.openrouter_client import client
from app.settings.config import settings


async def get_embedding(text: str) -> list[float]:
    """Эмбеддинг одного текста — используется для запроса пользователя при retrieval."""
    response = await client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=text,
        extra_body={"usage": {"include": True}},
    )
    log_embedding_call("embeddings.get_embedding", 1, response)
    return response.data[0].embedding


async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Эмбеддинги пачкой — используется при индексации базы знаний.
    """
    if not texts:
        return []
    response = await client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
        extra_body={"usage": {"include": True}},
    )
    log_embedding_call("embeddings.get_embeddings_batch", len(texts), response)
    return [item.embedding for item in response.data]