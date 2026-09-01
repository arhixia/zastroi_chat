import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk
from app.services.ai.embeddings import get_embedding

# Косинусное расстояние: 0 — идентичные по смыслу, 2 — противоположные.
DEFAULT_MAX_DISTANCE = 0.6


async def retrieve_chunks(
    db: AsyncSession,
    site_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    max_distance: float = DEFAULT_MAX_DISTANCE,
) -> list[tuple[Chunk, float]]:
    """
    Возвращает top_k активных чанков сайта, ближайших по смыслу к запросу,
    отсеивая те, что дальше max_distance — это и есть механизм
    "нет подтверждённой информации, не выдумываем".
    """
    query_embedding = await get_embedding(query)

    stmt = (
        select(Chunk, Chunk.embedding.cosine_distance(query_embedding).label("distance"))
        .where(Chunk.site_id == site_id, Chunk.is_active.is_(True))
        .order_by("distance")
        .limit(top_k)
    )
    result = await db.execute(stmt)

    return [(chunk, distance) for chunk, distance in result.all() if distance <= max_distance]