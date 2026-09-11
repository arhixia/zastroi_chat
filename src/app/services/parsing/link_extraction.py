from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


def _normalize_domain(netloc: str) -> str:
    return netloc.lower().removeprefix("www.")


def normalize_url(url: str) -> str:
    """Убирает фрагменты (#anchor) и trailing slash."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") if parsed.path != "/" else "/"
    return parsed._replace(fragment="", path=path).geturl()


def _extract_path(url: str) -> str:
    """
    Возвращает только путь URL (без схемы/домена), без trailing slash.
    Работает как для полных URL ('http://site.ru/x'), так и для
    "голых" путей, введённых пользователем ('/x').
    """
    parsed = urlparse(url)
    path = parsed.path
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return path


def is_excluded(url: str, excluded_paths: set[str]) -> bool:
    """
    Проверяет, попадает ли url под одно из исключений.
    Исключения могут быть заданы как путь без расширения ('/infrastructure'),
    как полный путь ('/infrastructure.html') или как каталог-префикс ('/news').
    Совпадение: точное равенство ИЛИ путь страницы начинается с
    исключённого пути и сразу за ним идёт '/', '.', '?' или конец строки
    (чтобы '/infra' не считался совпадением для '/infrastructure.html').
    """
    page_path = _extract_path(url)
    for excluded in excluded_paths:
        if not excluded:
            continue
        excluded_norm = excluded if excluded.startswith("/") else "/" + excluded
        excluded_norm = excluded_norm.rstrip("/") or "/"

        if page_path == excluded_norm:
            return True

        if page_path.startswith(excluded_norm):
            boundary = page_path[len(excluded_norm):len(excluded_norm) + 1]
            if boundary in ("", "/", ".", "?"):
                return True

    return False


def extract_links(html: str, base_url: str, allowed_domain: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    
    target_domain = allowed_domain.lower().split(":")[0].removeprefix("www.")
    
    links: list[str] = []
    seen: set[str] = set()

    print(f"[LINKS] Ищу ссылки на странице: {base_url}")
    print(f"[LINKS] Разрешенный домен: {target_domain}")

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()

        if not href or href.startswith(("mailto:", "tel:", "javascript:", "#", "data:")):
            continue

        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)

        if parsed.scheme not in ("http", "https"):
            continue
  
        link_domain = parsed.netloc.lower().split(":")[0].removeprefix("www.")
        
        if link_domain != target_domain:
            print(f"Отсеяно (другой домен): {absolute} (link={link_domain} != target={target_domain})")
            continue

        normalized = normalize_url(absolute)

        if normalized not in seen:
            seen.add(normalized)
            links.append(normalized)
            print(f"Найдена ссылка: {normalized}")

    print(f"[LINKS] Итого найдено {len(links)} уникальных ссылок")
    return links