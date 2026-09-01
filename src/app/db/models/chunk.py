import enum
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, DateTime, func, ForeignKey, Text, Integer, Boolean
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.settings.config import settings
from app.db.database import Base


class SourceType(str, enum.Enum):
    page = "page"
    document = "document"


class Chunk(Base):
    """
    Кусок текста с эмбеддингом — единица поиска для RAG.
    source_id указывает на Page.id или Document.id в зависимости от source_type.
    """
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)

    source_type: Mapped[SourceType] = mapped_column(SAEnum(SourceType), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # человекочитаемое название источника для ответа вида "Подробнее: [ЖК Ромашка]"
    source_label: Mapped[str] = mapped_column(String(512), nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.EMBEDDING_DIM))

    # выключается, когда источник помечен stale/excluded — не удаляем, чтобы не пересчитывать эмбеддинги зря
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())