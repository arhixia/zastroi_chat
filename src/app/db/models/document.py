import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.db.database import Base


class DocumentType(str, enum.Enum):
    pdf = "pdf"
    doc = "doc"
    docx = "docx"
    txt = "txt"
    xls = "xls"
    xlsx = "xlsx"


class DocumentStatus(str, enum.Enum):
    active = "active"
    excluded = "excluded"  # удалено/отключено администратором


class Document(Base):
    """Документ, загруженный вручную в базу знаний (PDF/DOC/DOCX/TXT/XLS/XLSX)."""
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)

    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[DocumentType] = mapped_column(SAEnum(DocumentType), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(SAEnum(DocumentStatus), default=DocumentStatus.active)
    
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    site = relationship("Site", back_populates="documents")