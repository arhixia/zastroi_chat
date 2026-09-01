import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Conversation(Base):
    """Диалог пользователя с ботом + маркетинговые метаданные визита."""
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )

    session_id: Mapped[str] = mapped_column(String(64), nullable=False)  # хранится у виджета (localStorage/cookie)
    visitor_id: Mapped[str] = mapped_column(String(64), nullable=False)  # долгоживущий идентификатор посетителя

    first_page_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    current_page_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    referrer: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    utm: Mapped[dict] = mapped_column(JSONB, default=dict)
    gclid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    yclid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metrika_client_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    device_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    browser: Mapped[str | None] = mapped_column(String(64), nullable=True)
    os: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)

    # снэп определённого интереса: {"жк": "...", "объект": "..."}
    detected_interest: Mapped[dict] = mapped_column(JSONB, default=dict)
    # счётчик для правила 
    messages_since_last_offer: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )