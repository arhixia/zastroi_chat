
import enum
import uuid
from datetime import datetime
 
from sqlalchemy import String, DateTime, func, ForeignKey, Boolean
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
 
from app.db.database import Base


class PageStatus(str, enum.Enum):
    active = "active"      # используется в ответах бота
    stale = "stale"        # пропала с сайта при повторном обходе 
    excluded = "excluded"  # исключена администратором вручную


class Page(Base):
    """Страница сайта, обработанная парсером."""
    __tablename__ = "pages"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
 
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
 
    # sha256 нормализованного текстового контента — по нему определяем "изменилась/не изменилась" страница
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
 
    status: Mapped[PageStatus] = mapped_column(SAEnum(PageStatus), default=PageStatus.active)
    is_relevant: Mapped[bool] = mapped_column(Boolean, default=True)  # результат ИИ-классификации на этапе парсинга
 
    last_crawled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

