import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ai.logging_utils import log_chat_call
from app.services.ai.openrouter_client import client
from app.services.knowledge_base.retrieval import retrieve_chunks
from app.settings.config import settings

logger = logging.getLogger("rag")

NO_INFO_ANSWER = (
    "К сожалению, точной информации по этому вопросу сейчас нет. "
    "Но вы можете оставить номер телефона — наш менеджер всё уточнит и перезвонит!"
)


SYSTEM_PROMPT = """Ты — дружелюбный и профессиональный консультант застройщика. Отвечай ТОЛЬКО на основе предоставленного КОНТЕКСТА.

Правила:
1. Отвечай кратко, по делу и понятным языком. Не используй канцеляризмы.
2. Если вопрос не о недвижимости (ЖК, цены, планировки) — вежливо ответь, что твоя специализация — объекты этого застройщика.
3. Если в КОНТЕКСТЕ нет ответа — честно скажи об этом и предложи оставить контакты для уточнения у менеджера.
4. Никогда не придумывай факты, которых нет в тексте."""


CLASSIFY_LEAD_RESPONSE_PROMPT = """
Ты анализируешь сообщение пользователя, который находится в диалоге с ботом-консультантом.
Бот только что попросил пользователя оставить контакты (имя или телефон).

Классифицируй сообщение пользователя в одну из категорий:
1. "NAME" - если это имя (или фраза типа "меня зовут...").
2. "PHONE" - если это номер телефона.
3. "REFUSAL" - если это отказ ("не надо", "отстань", "нет"), грубость или нерелевантный набор символов.
4. "QUESTION" - если пользователь проигнорировал просьбу и задал новый вопрос по ЖК.

Ответь ТОЛЬКО одним словом: NAME, PHONE, REFUSAL или QUESTION.

Сообщение пользователя: {message}
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
        return "QUESTION" # В случае ошибки считаем вопросом


    
async def answer_question(db: AsyncSession, site_id: uuid.UUID, question: str) -> dict:
    if any(kw in question.lower() for kw in ["оставить заявку", "перезвоните", "менеджер", "контакты"]):
        return {
            "answer": "Конечно! Сейчас я запрошу ваше имя для оформления заявки.",
            "sources": [],
            "ask_lead": True
        }

    matches = await retrieve_chunks(db, site_id, question)
    
    if matches:
        logger.info(f"[RAG] Найдено {len(matches)} чанков для запроса: '{question}'")
    else:
        logger.warning(f"[RAG] Ничего не найдено для: '{question}'")

    if not matches:
        return {"answer": NO_INFO_ANSWER, "sources": [], "ask_lead": True}

    context = "\n\n".join([f"[{c.source_label}]: {c.content}" for c, _ in matches])
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"КОНТЕКСТ:\n{context}\n\nВОПРОС: {question}"}
    ]

    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=600,
    )
    
    answer_text = response.choices[0].message.content
    sources = list({c.source_label for c, _ in matches})
    
    ask_lead = any(kw in answer_text.lower() for kw in ["оставьте", "менеджер свяжется", "уточнит"]) or \
               any(kw in question.lower() for kw in ["цена", "стоимость", "купить"])

    return {"answer": answer_text, "sources": sources, "ask_lead": ask_lead}