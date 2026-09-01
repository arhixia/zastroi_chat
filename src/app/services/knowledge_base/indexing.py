import uuid
 
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
 
from app.db.models import Chunk, SourceType
from app.services.knowledge_base.chunking import count_tokens, split_into_chunks
from app.services.ai.embeddings import get_embeddings_batch


async def index_text(
    db: AsyncSession,
    site_id: uuid.UUID,
    source_type: SourceType,
    source_id: uuid.UUID,
    source_label: str,
    text: str,
) -> int:
    """
    Разбивает текст источника (страницы или документа) на чанки,
    получает эмбеддинги и сохраняет их в БД.
 
    Возвращает количество созданных чанков.
    """
    pieces = split_into_chunks(text)

    if not pieces:
        return 0 

    await db.execute(
        update(Chunk)
        .where(Chunk.source_type == source_type, Chunk.source_id == source_id)
        .values(is_active=False)
    )

    embeddings = await get_embeddings_batch(pieces)
 
    for piece, embedding in zip(pieces, embeddings):
        db.add(
            Chunk(
                site_id=site_id,
                source_type=source_type,
                source_id=source_id,
                source_label=source_label,
                content=piece,
                token_count=count_tokens(piece),
                embedding=embedding,
                is_active=True,
            )
        )
 
    await db.commit()
    return len(pieces)

