from pathlib import Path
import uuid
from sqlalchemy import select
from app.db.models.chunk import SourceType
from app.db.models.document import Document
from app.db.session import AsyncSessionLocal 
from app.db.models import CrawlRun, CrawlStatus, Site
from app.services.knowledge_base.indexing import index_text
from app.services.parsing.crawler import run_crawl
from app.services.parsing.document_parsing import extract_text


async def start_crawl_job(ctx, site_id_str: str, crawl_run_id_str: str):
    print(f"[WORKER] Задача получена! Сайт: {site_id_str}")
    
    site_id = uuid.UUID(site_id_str)
    crawl_run_id = uuid.UUID(crawl_run_id_str)
    
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Site).where(Site.id == site_id))
            site = result.scalar_one_or_none()
            if not site: raise ValueError("Site not found")

            print(f"⚙️ [WORKER] Запускаю обход страниц для {site.domain}...")
            await run_crawl(db, site)
            
            print(f"[WORKER] Начинаю индексацию загруженных файлов...")
            docs_result = await db.execute(
                select(Document).where(
                    Document.site_id == site_id, 
                    Document.status == "active"
                )
            )
            documents = docs_result.scalars().all()
            
            for doc in documents:
                try:
                    file_path_str = doc.storage_path
                    if not file_path_str.startswith("/"):
                        file_path_str = f"/app/{file_path_str}"
                    
                    file_path = Path(file_path_str)
                    
                    if not file_path.exists():
                        print(f"[WORKER] Файл не найден по пути: {file_path}")
                        continue

                    print(f"[WORKER] Читаю файл: {doc.filename}")
                    text = extract_text(file_path, doc.file_type)
                    
                    if text.strip():
                        await index_text(
                            db=db,
                            site_id=site.id,
                            source_type=SourceType.document,
                            source_id=doc.id,
                            source_label=doc.filename,
                            text=text
                        )
                        print(f"[WORKER] Файл {doc.filename} проиндексирован")
                    else:
                        print(f"[WORKER] Файл {doc.filename} пуст")
                        
                except Exception as e:
                    print(f"[WORKER] Ошибка файла {doc.filename}: {e}")

            await db.commit()
            print(f"[WORKER] Полный цикл завершен")
            
        except Exception as e:
            print(f"[WORKER] Ошибка задачи: {e}")
            raise e