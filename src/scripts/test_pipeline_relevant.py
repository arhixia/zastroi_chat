"""
Тест положительной ветки pipeline: скармливаем HTML, который явно ПРО
недвижимость, и проверяем, что ИИ-классификация пропускает его и он
реально доходит до чанков в БД. Дополняет test_crawler.py — там
проверялась только отрицательная ветка (example.com не про недвижимость).

Запуск:
    docker compose exec api sh -c "cd src && python scripts/test_pipeline_relevant.py"
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.db.models import Chunk, Page, Site
from app.db.session import AsyncSessionLocal
from app.services.parsing.pipeline import process_fetched_page

TEST_DOMAIN = "test-relevant.local"

FAKE_HTML = """
<html><head><title>ЖК Ромашка — купить квартиру</title></head>
<body>
<nav><a href="/">Главная</a><a href="/about">О нас</a></nav>
<header><h1>Сайт застройщика</h1></header>
<main>
<article>
<h1>ЖК Ромашка</h1>
<p>Современный жилой комплекс комфорт-класса в 10 минутах от метро Октябрьская.</p>
<p>Квартиры от 35 до 120 квадратных метров. Стоимость студии от 6 500 000 рублей.</p>
<p>Срок сдачи — четвёртый квартал 2027 года. Парковка подземная.</p>
</article>
</main>
<footer>© 2026 Застройщик. Политика конфиденциальности.</footer>
</body></html>
"""


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Site).where(Site.domain == TEST_DOMAIN))
        site = result.scalar_one_or_none()
        if site is None:
            site = Site(name="Тест положительной классификации", domain=TEST_DOMAIN)
            db.add(site)
            await db.commit()
            await db.refresh(site)

        outcome = await process_fetched_page(db, site, "https://test-relevant.local/zhk/romashka", FAKE_HTML)
        print("Результат pipeline:", outcome)

        page_result = await db.execute(select(Page).where(Page.site_id == site.id))
        page = page_result.scalar_one()
        print(f"\nPage: is_relevant={page.is_relevant}, status={page.status.value}, title={page.title!r}")

        chunks_result = await db.execute(select(Chunk).where(Chunk.site_id == site.id))
        chunks = chunks_result.scalars().all()
        print(f"Чанков в БД: {len(chunks)}")
        for c in chunks:
            print(f"  - {c.content[:80]!r}")


if __name__ == "__main__":
    asyncio.run(main())