import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func, ForeignKey, Integer
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class CrawlStatus(str, enum.Enum):
    running = "running"
    success = "success"
    failed = "failed"
    partial = "partial"  # завершился, но часть страниц дала ошибку


class CrawlRun(Base):
    """История запусков парсинга сайта."""
    __tablename__ = "crawl_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)

    status: Mapped[CrawlStatus] = mapped_column(SAEnum(CrawlStatus), default=CrawlStatus.running)
    pages_processed: Mapped[int] = mapped_column(Integer, default=0)
    pages_added: Mapped[int] = mapped_column(Integer, default=0)
    pages_updated: Mapped[int] = mapped_column(Integer, default=0)
    pages_stale: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[list] = mapped_column(JSONB, default=list)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)