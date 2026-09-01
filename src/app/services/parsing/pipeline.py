import hashlib
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Page, PageStatus, Site, SourceType
from app.services.ai.classification import is_relevant_page
from app.services.knowledge_base.indexing import index_text
from app.services.parsing.content_extraction import extract_main_text, extract_title


async def process_fetched_page(db: AsyncSession, site: Site, url: str, html: str) -> dict:
    title = extract_title(html)
    text = extract_main_text(html)
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

    result = await db.execute(select(Page).where(Page.site_id == site.id, Page.url == url))
    page = result.scalar_one_or_none()
    is_new = page is None
    if is_new:
        page = Page(site_id=site.id, url=url)
        db.add(page)

    changed = is_new or page.content_hash != content_hash

    page.title = title
    page.content_hash = content_hash
    page.status = PageStatus.active
    page.last_crawled_at = datetime.now(timezone.utc)

    if not text.strip():
        page.is_relevant = False
        await db.commit()
        return {"url": url, "action": "skipped", "reason": "пустой текст после очистки"}

    relevant = await is_relevant_page(url, title, text)
    page.is_relevant = relevant
    await db.commit()
    await db.refresh(page)

    if not relevant:
        return {"url": url, "action": "skipped", "reason": "не относится к ЖК/объектам"}

    if not changed:
        return {"url": url, "action": "unchanged"}

    n_chunks = await index_text(
        db=db,
        site_id=site.id,
        source_type=SourceType.page,
        source_id=page.id,
        source_label=title or url,
        text=text,
    )
    return {"url": url, "action": "added" if is_new else "updated", "chunks": n_chunks}