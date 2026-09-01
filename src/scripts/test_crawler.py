"""
Полный тест краулера: создаёт тестовый сайт с стартовым URL, запускает
обход и печатает статистику CrawlRun.

Использует реальный ИИ (классификация страниц + эмбеддинги) — нужен
рабочий OPENROUTER_API_KEY в .env.

example.com выбран специально: у него одна страница со ссылкой на другой
домен (iana.org) — обход сам остановится после 1 страницы, безопасно
для теста, не уйдёт бесконтрольно вглубь чужого сайта.

Запуск:
    docker compose exec api sh -c "cd src && python scripts/test_crawler.py"
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.db.models import Site
from app.db.session import AsyncSessionLocal
from app.services.parsing.crawler import run_crawl

TEST_DOMAIN = "example.com"


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Site).where(Site.domain == TEST_DOMAIN))
        site = result.scalar_one_or_none()

        if site is None:
            site = Site(
                name="Example (тест краулера)",
                domain=TEST_DOMAIN,
                crawl_start_urls=["https://example.com"],
                crawl_excluded_urls=[],
            )
            db.add(site)
        else:
            site.crawl_start_urls = ["https://example.com"]

        await db.commit()
        await db.refresh(site)

        print(f"Сайт: {site.id} ({site.domain})")
        print(f"Стартовые URL: {site.crawl_start_urls}\n")

        crawl_run = await run_crawl(db, site, max_pages=20)

        print("=" * 60)
        print(f"Статус обхода: {crawl_run.status.value}")
        print(f"Обработано страниц: {crawl_run.pages_processed}")
        print(f"Добавлено: {crawl_run.pages_added}")
        print(f"Обновлено: {crawl_run.pages_updated}")
        print(f"Помечено неактуальными: {crawl_run.pages_stale}")
        print(f"Ошибок: {len(crawl_run.errors)}")
        for err in crawl_run.errors:
            print(f"  - {err}")


if __name__ == "__main__":
    asyncio.run(main())