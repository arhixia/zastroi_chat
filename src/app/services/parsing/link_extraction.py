from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


def normalize_url(url: str) -> str:
    return urlparse(url)._replace(fragment="").geturl()


def _normalize_domain(netloc: str) -> str:
    return netloc.lower().removeprefix("www.")


def extract_links(html: str, base_url: str, allowed_domain: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    target_domain = _normalize_domain(allowed_domain)

    links: list[str] = []
    seen: set[str] = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue

        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)

        if parsed.scheme not in ("http", "https"):
            continue
        if _normalize_domain(parsed.netloc) != target_domain:
            continue

        normalized = normalize_url(absolute)
        if normalized not in seen:
            seen.add(normalized)
            links.append(normalized)

    return links