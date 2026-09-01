import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Lead(Base):
    """Заявка (оставленные имя+телефон+согласие)"""
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    consent_given_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # версия/текст согласия на момент подтверждения
    consent_text_version: Mapped[str] = mapped_column(String(32), nullable=False)

    interest: Mapped[dict] = mapped_column(JSONB, default=dict)  # снимок интереса на момент заявки

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())