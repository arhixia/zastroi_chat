"""
Ручной сквозной тест RAG-пайплайна: создаёт тестовый сайт, индексирует
пример текста базы знаний и прогоняет через него несколько вопросов —
в тему с ответом, в тему без ответа, не по теме.

Печатает не только финальный ответ, но и "сырые" расстояния до ближайших
чанков — по ним и калибруется DEFAULT_MAX_DISTANCE в retrieval.py.

ВАЖНО: делает реальные запросы к OpenRouter (эмбеддинги + чат) —
нужен рабочий OPENROUTER_API_KEY в .env, и это стоит небольших денег.

Запуск (контейнер api должен быть поднят), любой из двух вариантов:
    docker compose exec api sh -c "cd src && python -m scripts.test_rag"
    docker compose exec api sh -c "cd src && python scripts/test_rag.py"
"""
import asyncio
import os
import sys
import uuid

# Гарантируем, что src/ есть в sys.path, даже если скрипт запущен напрямую
# (python scripts/test_rag.py кладёт в sys.path только папку scripts/, не src/).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.db.models import Site, SourceType
from app.db.session import AsyncSessionLocal
from app.services.knowledge_base.indexing import index_text
from app.services.ai.rag import answer_question
from app.services.knowledge_base.retrieval import retrieve_chunks

TEST_DOMAIN = "test.local"

SAMPLE_TEXT = """ЖК Ромашка — современный жилой комплекс комфорт-класса в 10 минутах от метро Октябрьская.
Рядом школа №25 и детский сад "Солнышко".

В продаже квартиры от 35 до 120 квадратных метров: студии, однокомнатные, двухкомнатные и трёхкомнатные.
Стоимость студии от 6 500 000 рублей, однокомнатной — от 8 200 000 рублей.
Отделка чистовая, под ключ, входит в стоимость квартиры.

Срок сдачи дома — четвёртый квартал 2027 года. Разрешение на строительство получено, стройка ведётся по графику.

Парковка подземная, машиноместа продаются отдельно от квартир, стоимость от 800 000 рублей.
Ипотека доступна по программе господдержки от 6 банков-партнёров."""

QUESTIONS = [
    "Сколько стоит студия в ЖК Ромашка?",         # ответ есть в тексте
    "Когда сдача дома?",                            # ответ есть в тексте
    "Какая погода в Москве сегодня?",               # не по теме — должен вежливо отказать
    "Есть скидка 90% при покупке за наличные?",     # похоже на тему, но данных нет — не должен придумывать
]


async def main() -> None:
    async with AsyncSessionLocal() as db:
        # 1. находим или создаём тестовый сайт
        result = await db.execute(select(Site).where(Site.domain == TEST_DOMAIN))
        site = result.scalar_one_or_none()
        if site is None:
            site = Site(name="Тестовый сайт", domain=TEST_DOMAIN)
            db.add(site)
            await db.commit()
            await db.refresh(site)
            print(f"Создан тестовый сайт: {site.id}")
        else:
            print(f"Используем существующий тестовый сайт: {site.id}")

        # 2. индексируем тестовый текст как "страницу"
        page_id = uuid.uuid4()
        n_chunks = await index_text(
            db=db,
            site_id=site.id,
            source_type=SourceType.page,
            source_id=page_id,
            source_label="ЖК Ромашка — страница на сайте",
            text=SAMPLE_TEXT,
        )
        print(f"Проиндексировано чанков: {n_chunks}\n")

        # 3. прогоняем тестовые вопросы
        for question in QUESTIONS:
            print("=" * 70)
            print(f"ВОПРОС: {question}")

            # max_distance=2.0 — показываем ВСЕ расстояния без отсечки, для калибровки порога
            raw_matches = await retrieve_chunks(db, site.id, question, top_k=5, max_distance=2.0)
            print("Расстояния до ближайших чанков (для калибровки max_distance):")
            for chunk, distance in raw_matches:
                preview = chunk.content[:60].replace("\n", " ")
                print(f"  {distance:.3f}  |  {preview}...")

            answer = await answer_question(db, site.id, question)
            print(f"\nОТВЕТ: {answer['answer']}")
            print(f"ИСТОЧНИКИ: {answer['sources']}")
            print()


if __name__ == "__main__":
    asyncio.run(main())