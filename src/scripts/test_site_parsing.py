"""
Тест получения HTML через Playwright (site_parsing.PlaywrightFetcher).
Проверяет и успешную загрузку страницы (с JS-рендерингом), и обработку
ошибок — 404 и несуществующий домен.

Не требует OPENROUTER_API_KEY — этот модуль вообще не обращается к ИИ,
только к браузеру и к тестовым сайтам.

Запуск (контейнер api должен быть поднят и пересобран с Chromium):
    docker compose exec api sh -c "cd src && python scripts/test_site_parsing.py"
"""
import asyncio
import os
import sys

# Гарантируем, что src/ есть в sys.path, даже если скрипт запущен напрямую.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.parsing.site_parsing import PageFetchError, PlaywrightFetcher

TEST_URLS = [
    "https://example.com",                                    # простая статическая страница — должна пройти
    "https://httpbin.org/status/404",                          # должен поймать PageFetchError (статус 404)
    "https://this-domain-does-not-exist-zastroi-test.ru",      # должен поймать ошибку — домен не существует
]


async def main() -> None:
    async with PlaywrightFetcher(timeout_ms=15_000) as fetcher:
        for url in TEST_URLS:
            print("=" * 70)
            print(f"URL: {url}")
            try:
                html = await fetcher.fetch(url)
                print(f"OK: получено {len(html)} символов HTML")
                preview = html[:300].replace("\n", " ")
                print(f"Превью: {preview}...")
            except PageFetchError as e:
                print(f"ОЖИДАЕМАЯ ОШИБКА: {e}")


if __name__ == "__main__":
    asyncio.run(main())