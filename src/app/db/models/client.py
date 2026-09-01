import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Client(Base):
    """
    Карточка клиента — объединяет все диалоги и заявки одного номера телефона
    в рамках одного сайта.
    """
    __tablename__ = "clients"
    __table_args__ = (UniqueConstraint("site_id", "phone", name="uq_client_site_phone"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)

    phone: Mapped[str] = mapped_column(String(20), nullable=False)  # нормализованный формат +7XXXXXXXXXX
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )