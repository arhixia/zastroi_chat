import uuid
from sqlalchemy import select
from app.db.session import AsyncSessionLocal 
from app.db.models import CrawlRun, CrawlStatus, Site
from app.services.parsing.crawler import run_crawl

async def start_crawl_job(ctx, site_id_str: str, crawl_run_id_str: str):
    print(f"[WORKER] Задача получена! Начинаем обработку сайта {site_id_str}")
    
    site_id = uuid.UUID(site_id_str)
    crawl_run_id = uuid.UUID(crawl_run_id_str)
    
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Site).where(Site.id == site_id))
            site = result.scalar_one_or_none()
            
            if not site:
                print(f"[WORKER] Ошибка: Сайт с ID {site_id} не найден в базе!")
                return

            print(f"[WORKER] Сайт найден: {site.name}. Запускаю краулер...")
            
            await run_crawl(db, site)
            
        except Exception as e:
            print(f"[WORKER] Критическая ошибка в задаче: {e}")
            raise e