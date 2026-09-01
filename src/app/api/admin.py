import csv
import io
from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, update

from app.settings.config import settings
from app.api.auth.deps import CurrentUser, DbSession
from app.api.auth.auth import get_password_hash
from app.api.sites import _get_site_or_404
from app.db.models.admin import Admin
from app.db.models.chunk import Chunk, SourceType
from app.db.models.crawl_run import CrawlRun, CrawlStatus
from app.db.models.document import Document, DocumentStatus, DocumentType
from app.db.models.lead import Lead
from app.db.models.page import Page, PageStatus
from app.db.models.site import Site
from app.schemas.site import SiteCreate, SiteOut, SiteUpdate, WidgetSnippetOut
from app.workers.tasks import start_crawl_task

router = APIRouter(prefix="/admin", tags=["Admin"])


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# --- Управление сайтами ---

@router.post("/sites", response_model=SiteOut, status_code=status.HTTP_201_CREATED)
async def create_site(payload: SiteCreate, db: DbSession, _: CurrentUser):
    existing = await db.execute(select(Site).where(Site.domain == payload.domain))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Домен уже занят")
    
    site = Site(**payload.model_dump())
    db.add(site)
    await db.commit()
    await db.refresh(site)
    return site


@router.get("/sites", response_model=list[SiteOut])
async def list_sites(db: DbSession, _: CurrentUser):
    result = await db.execute(select(Site).order_by(Site.created_at.desc()))
    return result.scalars().all()


@router.patch("/sites/{site_id}", response_model=SiteOut)
async def update_site(site_id: uuid.UUID, payload: SiteUpdate, db: DbSession, _: CurrentUser):
    site = await _get_site_or_404(db, site_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(site, field, value)
    await db.commit()
    await db.refresh(site)
    return site


@router.delete("/sites/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(site_id: uuid.UUID, db: DbSession, _: CurrentUser):
    site = await _get_site_or_404(db, site_id)
    await db.delete(site)
    await db.commit()


@router.get("/sites/{site_id}/snippet", response_model=WidgetSnippetOut)
async def get_widget_snippet(site_id: uuid.UUID, db: DbSession, _: CurrentUser):
    site = await _get_site_or_404(db, site_id)
    snippet = f'<script src="{settings.WIDGET_SCRIPT_URL}" data-site-id="{site.id}" async></script>'
    return WidgetSnippetOut(site_id=site.id, snippet=snippet)


# --- Парсинг и База Знаний ---

@router.post("/sites/{site_id}/crawl", status_code=status.HTTP_202_ACCEPTED)
async def trigger_crawl(site_id: uuid.UUID, db: DbSession, _: CurrentUser):
    site = await _get_site_or_404(db, site_id)
    run = CrawlRun(site_id=site.id, status=CrawlStatus.running)
    db.add(run)
    await db.commit()
    await db.refresh(run)
    start_crawl_task.delay(str(site.id), str(run.id))
    return {"run_id": str(run.id)}


@router.get("/sites/{site_id}/crawls")
async def get_crawl_history(site_id: uuid.UUID, db: DbSession, _: CurrentUser):
    result = await db.execute(
        select(CrawlRun).where(CrawlRun.site_id == site_id).order_by(CrawlRun.started_at.desc()).limit(20)
    )
    return result.scalars().all()

@router.post("/sites/{site_id}/documents", status_code=status.HTTP_201_CREATED)
async def upload_document(site_id: uuid.UUID, file: UploadFile = File(...), db: DbSession = Depends(), _: CurrentUser = Depends()):
    site = await _get_site_or_404(db, site_id)
    
    ext = Path(file.filename).suffix.lower()
    type_map = {".pdf": DocumentType.pdf, ".docx": DocumentType.docx, ".xlsx": DocumentType.xlsx, ".txt": DocumentType.txt}
    doc_type = type_map.get(ext)
    
    if not doc_type:
        raise HTTPException(400, "Неподдерживаемый формат. Используйте PDF, DOCX, XLSX, TXT")

    file_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    doc = Document(site_id=site.id, filename=file.filename, file_type=doc_type, storage_path=str(file_path))
    db.add(doc)
    await db.commit()
    return {"id": str(doc.id), "filename": doc.filename}



@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(source_id: uuid.UUID, source_type: str, db: DbSession, _: CurrentUser):
    """Отключает источник (страницу или документ) из базы знаний."""
    model = Page if source_type == "page" else Document
    src_enum = SourceType.page if source_type == "page" else SourceType.document
    
    result = await db.execute(select(model).where(model.id == source_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(404, "Источник не найден")

    if hasattr(item, 'status'):
        item.status = PageStatus.excluded if source_type == "page" else DocumentStatus.excluded
    
    await db.execute(update(Chunk).where(Chunk.source_id == source_id, Chunk.source_type == src_enum).values(is_active=False))
    await db.commit()


# --- Лиды и Аналитика ---

@router.get("/leads")
async def get_leads(db: DbSession, _: CurrentUser, phone: str | None = None):
    query = select(Lead).join_from(Lead, Site, Lead.site_id == Site.id)
    if phone:
        query = query.where(Lead.phone.contains(phone.replace(" ", "")))
    
    result = await db.execute(query.order_by(Lead.created_at.desc()))
    return result.scalars().all()


@router.get("/leads/export/csv")
async def export_leads_csv(db: DbSession, _: CurrentUser):
    """Выгрузка всех лидов в CSV."""
    result = await db.execute(select(Lead).order_by(Lead.created_at.desc()))
    leads = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Имя", "Телефон", "Дата", "Интерес", "Сайт"])
    
    for lead in leads:
        writer.writerow([
            str(lead.id), 
            lead.name, 
            lead.phone, 
            lead.created_at.strftime("%Y-%m-%d %H:%M"),
            str(lead.interest),
            lead.site_id 
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"}
    )