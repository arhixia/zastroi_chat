import uuid
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.db.models import CrawlRun, CrawlStatus, Site
from app.services.parsing.crawler import run_crawl


@shared_task(bind=True, max_retries=3)
def start_crawl_task(self, site_id_str: str, crawl_run_id_str: str):
    """
    Фоновая задача для парсинга сайта.
    """
    site_id = uuid.UUID(site_id_str)
    crawl_run_id = uuid.UUID(crawl_run_id_str)
    
    import asyncio
    
    async def _crawl():
        async with AsyncSessionLocal() as db:
            try:
                from sqlalchemy import select
                result = await db.execute(select(Site).where(Site.id == site_id))
                site = result.scalar_one_or_none()
                
                if not site:
                    raise ValueError(f"Site {site_id} not found")

                await run_crawl(db, site)
                
            except Exception as exc:
                run_result = await db.execute(select(CrawlRun).where(CrawlRun.id == crawl_run_id))
                run_obj = run_result.scalar_one_or_none()
                if run_obj:
                    run_obj.status = CrawlStatus.failed
                    run_obj.errors.append({"error": str(exc)})
                    await db.commit()
                raise self.retry(exc=exc, countdown=60)

    asyncio.run(_crawl())