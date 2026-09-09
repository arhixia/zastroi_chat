import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ai.langchain_agent import get_smart_response
from app.services.ai.openrouter_client import client
from app.services.knowledge_base.retrieval import retrieve_chunks
from app.settings.config import settings

logger = logging.getLogger("rag")

CLASSIFY_LEAD_RESPONSE_PROMPT = """
Ты анализируешь сообщение пользователя. Бот попросил контакты.
Классифицируй сообщение:
1. "NAME" - имя.
2. "PHONE" - телефон.
3. "REFUSAL" - отказ или грубость.
4. "QUESTION" - новый вопрос по ЖК.
Ответь ТОЛЬКО одним словом.
Сообщение: {message}
"""

async def classify_lead_response(message: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": CLASSIFY_LEAD_RESPONSE_PROMPT.format(message=message)}],
            temperature=0,
            max_tokens=5,
        )
        return (response.choices[0].message.content or "").strip().upper()
    except:
        return "QUESTION"

    
async def answer_question(db: AsyncSession, site_id: uuid.UUID, question: str) -> dict:
    if any(kw in question.lower() for kw in ["оставить заявку", "перезвоните", "контакты"]):
        return {
            "answer": "Конечно! Пожалуйста, заполните форму ниже.",
            "sources": [],
            "ask_lead": True
        }

    matches = await retrieve_chunks(db, site_id, question)
    
    context = ""
    sources = []
    
    if matches:
        context = "\n\n".join([f"[{c.source_label}]: {c.content}" for c, _ in matches])
        sources = list({c.source_label for c, _ in matches})
    else:
        context = "Информация в базе знаний отсутствует."

    result = await get_smart_response(question, context=context)

    result["sources"] = sources
    
    return result