import csv
import io
from pathlib import Path
import uuid

from arq.connections import ArqRedis
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from app.db.models.conversation import Conversation
from app.schemas.widget import LeadOut
from app.settings.config import settings
from app.api.auth.deps import CurrentUser, DbSession
from app.api.auth.auth import get_password_hash
from app.api.sites import _get_site_or_404
from app.db.models.admin import Admin
from app.db.models.chunk import Chunk, SourceType
from app.db.models.message import Message
from app.db.models.crawl_run import CrawlRun, CrawlStatus
from app.db.models.document import Document, DocumentStatus, DocumentType
from app.db.models.lead import Lead
from app.db.models.page import Page, PageStatus
from app.db.models.site import Site
from app.schemas.site import SiteCreate, SiteOut, SiteUpdate, WidgetSnippetOut


router = APIRouter(prefix="/admin", tags=["Admin"])


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# --- Управление сайтами ---

@router.post("/sites", response_model=SiteOut, status_code=status.HTTP_201_CREATED)
async def create_site(payload: SiteCreate, db: DbSession, _: CurrentUser):
    start_urls = payload.crawl_start_urls.copy()
    if not start_urls:
        start_urls.append(f"https://{payload.domain}")
        
    site_data = payload.model_dump()
    site_data['crawl_start_urls'] = start_urls

    existing = await db.execute(select(Site).where(Site.domain == payload.domain))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Домен уже занят")
    
    site = Site(**site_data)
    db.add(site)
    await db.commit()
    
    result = await db.execute(
        select(Site)
        .where(Site.id == site.id)
        .options(joinedload(Site.documents))
    )
    site = result.scalars().first()
    
    return site


@router.get("/sites", response_model=list[SiteOut])
async def list_sites(db: DbSession, _: CurrentUser):
    result = await db.execute(
        select(Site)
        .options(joinedload(Site.documents))
        .order_by(Site.created_at.desc())
    )
    sites = result.scalars().unique().all()
    
    for site in sites:
        site.documents = [doc for doc in site.documents if doc.status == DocumentStatus.active]
        
    return sites


@router.patch("/sites/{site_id}", response_model=SiteOut)
async def update_site(site_id: uuid.UUID, payload: SiteUpdate, db: DbSession, _: CurrentUser):
    site = await _get_site_or_404(db, site_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(site, field, value)
    await db.commit()
    
    result = await db.execute(
        select(Site)
        .where(Site.id == site_id)
        .options(joinedload(Site.documents))
    )
    site = result.scalars().first()
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

async def get_arq_redis() -> ArqRedis:
    from arq.connections import create_pool
    from app.workers.worker_settings import WorkerSettings
    return await create_pool(WorkerSettings.redis_settings)


@router.post("/sites/{site_id}/crawl", status_code=status.HTTP_202_ACCEPTED)
async def trigger_crawl(
    site_id: uuid.UUID, 
    db: DbSession, 
    _: CurrentUser,
    redis: ArqRedis = Depends(get_arq_redis)
):
    site = await _get_site_or_404(db, site_id)
    
    run = CrawlRun(site_id=site.id, status=CrawlStatus.running)
    db.add(run)
    await db.commit()
    await db.refresh(run)
   
    await redis.enqueue_job('start_crawl_job', str(site.id), str(run.id))
    
    return {"run_id": str(run.id)}


@router.get("/sites/{site_id}/crawls")
async def get_crawl_history(site_id: uuid.UUID, db: DbSession, _: CurrentUser):
    result = await db.execute(
        select(CrawlRun).where(CrawlRun.site_id == site_id).order_by(CrawlRun.started_at.desc()).limit(20)
    )
    return result.scalars().all()


@router.post("/sites/{site_id}/documents", status_code=status.HTTP_201_CREATED)
async def upload_document(
    site_id: uuid.UUID,
    db: DbSession,
    _: CurrentUser,
    file: UploadFile = File(...),
):
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

@router.get("/leads", response_model=list[LeadOut])
async def get_leads(db: DbSession, _: CurrentUser, phone: str | None = None):
    query = select(Lead, Site.name).join_from(Lead, Site, Lead.site_id == Site.id)
    
    if phone:
        clean_phone = phone.replace(" ", "").replace("-", "")
        query = query.where(Lead.phone.contains(clean_phone))
    
    result = await db.execute(query.order_by(Lead.created_at.desc()))
    
    leads_out = []
    for lead, site_name in result.all():
        lead_dict = {
            "id": lead.id,
            "site_id": lead.site_id,
            "site_name": site_name,
            "name": lead.name,
            "phone": lead.phone,
            "interest": lead.interest,
            "created_at": lead.created_at
        }
        leads_out.append(lead_dict)
        
    return leads_out


@router.get("/leads/{lead_id}/details")
async def get_lead_details(lead_id: uuid.UUID, db: DbSession, _: CurrentUser):
    """Возвращает детали лида и историю переписки."""
    
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Заявка не найдена")

    conversation = await db.get(Conversation, lead.conversation_id)
    
    messages = []
    if conversation:
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
        )
        messages = result.scalars().all()

    return {
        "lead": lead,
        "conversation": conversation,
        "messages": messages
    }


@router.get("/leads/export/csv")
async def export_leads_csv(db: DbSession, _: CurrentUser):
    """Выгрузка лидов в красивом формате для Excel."""
    query = select(Lead, Site.name).join_from(Lead, Site, Lead.site_id == Site.id)
    result = await db.execute(query.order_by(Lead.created_at.desc()))
    
    output = io.StringIO()
    output.write('\ufeff') 
    
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(["Дата", "Сайт", "Имя клиента", "Телефон", "Последний вопрос"])
    
    for lead, site_name in result.all():
        last_question = "Не указан"
        if lead.interest and isinstance(lead.interest, dict):
            q = lead.interest.get("last_question", "")
            if q and len(q) > 2: 
                last_question = str(q).replace("\n", " ").strip()

        writer.writerow([
            lead.created_at.strftime("%d.%m.%Y %H:%M"),
            site_name,
            lead.name,
            lead.phone,
            last_question
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"}
    )