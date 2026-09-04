from collections import deque
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk, CrawlRun, CrawlStatus, Page, PageStatus, Site, SourceType
from app.services.parsing.link_extraction import extract_links, normalize_url
from app.services.parsing.pipeline import process_fetched_page
from app.services.parsing.site_parsing import PageFetchError, PlaywrightFetcher


async def run_crawl(db: AsyncSession, site: Site, max_pages: int = 200) -> CrawlRun:
    print(f"[CRAWLER] Запуск парсинга для сайта: {site.name} ({site.domain})")
    
    crawl_run = CrawlRun(site_id=site.id, status=CrawlStatus.running)
    db.add(crawl_run)
    await db.commit()
    await db.refresh(crawl_run)

    excluded = {normalize_url(u) for u in (site.crawl_excluded_urls or [])}
    start_urls = site.crawl_start_urls if site.crawl_start_urls else [f"https://{site.domain}"]
    queue: deque[str] = deque(normalize_url(u) for u in start_urls)
    
    visited: set[str] = set()
    found_urls: set[str] = set()

    added = updated = processed = 0
    errors: list[dict] = []

    async with PlaywrightFetcher() as fetcher:
        while queue and len(visited) < max_pages:
            url = queue.popleft()
            if url in visited or url in excluded:
                continue
            
            visited.add(url)
            print(f"[CRAWLER] Обработка ({len(visited)}/{max_pages}): {url}")

            try:
                html = await fetcher.fetch(url)
            except PageFetchError as e:
                print(f"[CRAWLER] Ошибка загрузки: {url} - {e}")
                errors.append({"url": url, "error": str(e)})
                continue

            found_urls.add(url)

            try:
                result = await process_fetched_page(db, site, url, html)
                action = result.get("action")
                
                if action == "added":
                    added += 1
                    print(f"[CRAWLER] Добавлено: {url} (чанков: {result.get('chunks', 0)})")
                elif action == "updated":
                    updated += 1
                    print(f"[CRAWLER] Обновлено: {url}")
                elif action == "skipped":
                    print(f"[CRAWLER] Пропущено: {url} ({result.get('reason')})")
                    
            except Exception as e:
                print(f"[CRAWLER] Ошибка обработки контента: {url} - {e}")
                errors.append({"url": url, "error": f"ошибка обработки: {e}"})
                continue

            processed += 1

            new_links = extract_links(html, base_url=url, allowed_domain=site.domain)
            for link in new_links:
                if link not in visited and link not in excluded:
                    queue.append(link)
            
            if new_links:
                print(f"[CRAWLER] Найдено {len(new_links)} новых ссылок на странице")

    print(f"[CRAWLER] Проверка устаревших страниц...")
    pages_stale = await _mark_stale_pages(db, site, found_urls)

    crawl_run.status = CrawlStatus.success if not errors else CrawlStatus.partial
    crawl_run.pages_processed = processed
    crawl_run.pages_added = added
    crawl_run.pages_updated = updated
    crawl_run.pages_stale = pages_stale
    crawl_run.errors = errors
    crawl_run.finished_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(crawl_run)

    print(f"[CRAWLER] Парсинг завершен! Обработано: {processed}, Добавлено: {added}, Устарело: {pages_stale}")
    return crawl_run


async def _mark_stale_pages(db: AsyncSession, site: Site, found_urls: set[str]) -> int:
    result = await db.execute(select(Page).where(Page.site_id == site.id, Page.status == PageStatus.active))
    pages = result.scalars().all()

    stale_count = 0
    for page in pages:
        if normalize_url(page.url) not in found_urls:
            page.status = PageStatus.stale
            stale_count += 1
            await db.execute(
                update(Chunk)
                .where(Chunk.source_type == SourceType.page, Chunk.source_id == page.id)
                .values(is_active=False)
            )

    await db.commit()
    return stale_count