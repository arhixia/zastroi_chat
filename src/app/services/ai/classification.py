from app.services.ai.logging_utils import log_chat_call
from app.services.ai.openrouter_client import client
from app.settings.config import settings

SYSTEM_PROMPT = """Ты определяешь, относится ли страница сайта застройщика к жилым комплексам, объектам недвижимости, квартирам, планировкам, ценам, срокам сдачи, инфраструктуре или условиям покупки.

Ответь одним словом: "да" или "нет".

"да" — если страница про ЖК, корпуса, квартиры, планировки, цены, сроки, инфраструктуру, ипотеку, акции на покупку.
"нет" — если это новости без информации об объектах, вакансии, общие статьи, юридические страницы (политика конфиденциальности, оферта), техническая страница (контакты, карта сайта, 404)."""


async def is_relevant_page(url: str, title: str, text: str) -> bool:
    preview = text[:1500]
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"URL: {url}\nЗаголовок: {title}\n\nТекст:\n{preview}"},
    ]

    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        temperature=0,
        max_tokens=5,
        extra_body={"usage": {"include": True}},
    )
    log_chat_call("classification.is_relevant_page", messages, response)

    answer = (response.choices[0].message.content or "").strip().lower()
    return answer.startswith("да")