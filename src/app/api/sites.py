import uuid
 
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
 
from app.api.auth.deps import CurrentUser, DbSession
from app.db.models.site import Site
from app.schemas.site import SiteCreate, SiteOut, SiteUpdate, WidgetSnippetOut
from app.settings.config import settings
 
router = APIRouter(prefix="/sites", tags=["Sites"])


@router.post("", response_model=SiteOut, status_code=status.HTTP_201_CREATED)
async def create_site(payload: SiteCreate, db: DbSession, _: CurrentUser):
    existing = await db.execute(select(Site).where(Site.domain == payload.domain))

    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Сайт с доменом {payload.domain} уже существует")
 
    site = Site(**payload.model_dump())
    db.add(site)
    await db.commit()
    await db.refresh(site)
    return site


@router.get("", response_model=list[SiteOut])
async def list_sites(db: DbSession, _: CurrentUser):
    result = await db.execute(select(Site).order_by(Site.created_at.desc()))
    return result.scalars().all()
 
 
async def _get_site_or_404(db: DbSession, site_id: uuid.UUID) -> Site:
    result = await db.execute(select(Site).where(Site.id == site_id))
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Сайт не найден")
    return site


@router.get("/{site_id}", response_model=SiteOut)
async def get_site(site_id: uuid.UUID, db: DbSession, _: CurrentUser):
    return await _get_site_or_404(db, site_id)


@router.patch("/{site_id}", response_model=SiteOut)
async def update_site(site_id: uuid.UUID, payload: SiteUpdate, db: DbSession, _: CurrentUser):
    site = await _get_site_or_404(db, site_id)
 
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(site, field, value)
 
    await db.commit()
    await db.refresh(site)
    return site
 
 
@router.post("/{site_id}/disable", response_model=SiteOut)
async def disable_site(site_id: uuid.UUID, db: DbSession, _: CurrentUser):
    site = await _get_site_or_404(db, site_id)
    site.is_active = False
    await db.commit()
    await db.refresh(site)
    return site
 
 
@router.post("/{site_id}/enable", response_model=SiteOut)
async def enable_site(site_id: uuid.UUID, db: DbSession, _: CurrentUser):
    site = await _get_site_or_404(db, site_id)
    site.is_active = True
    await db.commit()
    await db.refresh(site)
    return site
 
 
@router.get("/{site_id}/widget-snippet", response_model=WidgetSnippetOut)
async def get_widget_snippet(site_id: uuid.UUID, db: DbSession, _: CurrentUser):
    site = await _get_site_or_404(db, site_id)
 
    snippet = (
        f'<script src="{settings.WIDGET_SCRIPT_URL}" '
        f'data-site-id="{site.id}" async></script>'
    )
    return WidgetSnippetOut(site_id=site.id, snippet=snippet)



