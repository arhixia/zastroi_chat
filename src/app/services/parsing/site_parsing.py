"""
Получение HTML отрендеренной страницы через Playwright (п.5 ТЗ —
"поддержка обычных и JavaScript-рендеримых сайтов").
данных о квартирах, ценах и планировках.

"""
from playwright.async_api import Browser, BrowserContext, Page
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright


class PageFetchError(Exception):
    """Не удалось получить HTML страницы: таймаут, сетевая ошибка, статус 4xx/5xx."""


class PlaywrightFetcher:
    """
    Держит один браузер и один browser context открытыми на весь обход сайта —
    открывать новый браузер на каждую страницу дорого по времени и памяти,
    а сайт застройщика может содержать десятки/сотни страниц (п.5 ТЗ).

    Использование:
        async with PlaywrightFetcher() as fetcher:
            html = await fetcher.fetch("https://example.com/zhk/romashka")
    """

    def __init__(self, timeout_ms: int = 30_000, block_resources: bool = True):
        self.timeout_ms = timeout_ms
        self.block_resources = block_resources

        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def __aenter__(self) -> "PlaywrightFetcher":
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._context = await self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (compatible; ZastroiChatbotCrawler/1.0)"
            ),
            viewport={"width": 1366, "height": 900},
        )

        if self.block_resources:
            await self._context.route(
                "**/*",
                lambda route: route.abort()
                if route.request.resource_type in ("image", "font", "media")
                else route.continue_(),
            )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._context is not None:
            await self._context.close()
        if self._browser is not None:
            await self._browser.close()
        if self._playwright is not None:
            await self._playwright.stop()

    async def fetch(self, url: str) -> str:
        """
        Открывает страницу, дожидается загрузки (в т.ч. JS-рендеринга)
        и возвращает HTML уже после выполнения JS — через page.content(),
        а не "сырой" ответ сервера.
        """
        if self._context is None:
            raise RuntimeError("PlaywrightFetcher нужно использовать через 'async with'")

        page: Page = await self._context.new_page()
        try:
            response = await page.goto(url, wait_until="networkidle", timeout=self.timeout_ms)

            if response is None:
                raise PageFetchError(f"{url}: не удалось получить ответ от сервера")

            if response.status >= 400:
                raise PageFetchError(f"{url}: сервер вернул статус {response.status}")

            return await page.content()

        except PlaywrightTimeoutError as e:
            raise PageFetchError(f"{url}: таймаут загрузки ({self.timeout_ms} мс)") from e
        except PlaywrightError as e:
            raise PageFetchError(f"{url}: ошибка при загрузке страницы ({e})") from e
        finally:
            await page.close()