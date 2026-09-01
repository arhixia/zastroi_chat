import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Site(Base):
    """Сайт застройщика, подключённый к системе. Все данные изолируются по site_id."""
    __tablename__ = "sites"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    allowed_origins: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    crawl_start_urls: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    crawl_excluded_urls: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Настройки виджета (п.3, п.9 ТЗ — конфигурация через админку)
    widget_logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    widget_primary_color: Mapped[str] = mapped_column(String(16), default="#2563eb")
    widget_bot_name: Mapped[str] = mapped_column(String(100), default="Помощник")
    widget_welcome_message: Mapped[str] = mapped_column(String(1000), default="Здравствуйте! Чем могу помочь?")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )