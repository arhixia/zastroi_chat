from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


def _normalize_domain(netloc: str) -> str:
    return netloc.lower().removeprefix("www.")


def normalize_url(url: str) -> str:
    """Убирает фрагменты (#anchor) и trailing slash."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") if parsed.path != "/" else "/"
    return parsed._replace(fragment="", path=path).geturl()


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