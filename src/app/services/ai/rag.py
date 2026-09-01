import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.logging_utils import log_chat_call
from app.services.ai.openrouter_client import client
from app.services.knowledge_base.retrieval import retrieve_chunks
from app.settings.config import settings

NO_INFO_ANSWER = (
    "Точной информации по этому вопросу в базе знаний нет. "
    "Оставьте, пожалуйста, контакты — менеджер уточнит и свяжется с вами."
)

SYSTEM_PROMPT = """Ты — консультант застройщика на сайте. Отвечай ТОЛЬКО на русском языке.

Правила:
1. Отвечай только на основе текста в разделе КОНТЕКСТ ниже. Никогда не используй никакие другие знания и не додумывай факты.
2. Если в контексте нет ответа на вопрос — прямо скажи, что точной информации нет, и предложи оставить контакты для уточнения у менеджера.
3. Если разные фрагменты контекста противоречат друг другу — сообщи, что точной информации нет, и предложи связаться с менеджером. Никогда не выбирай одну из версий как достоверную и не пытайся угадать, какая правильная.
4. Если вопрос не связан с ЖК, объектами, квартирами, ценами, сроками, инфраструктурой или условиями покупки застройщика — вежливо ответь, что можешь помочь только с вопросами по объектам застройщика.
5. Если ответ основан на конкретном источнике из контекста — заверши ответ строкой вида: "Подробнее: [название источника]"."""


async def answer_question(db: AsyncSession, site_id: uuid.UUID, question: str) -> dict:
    """
    Основная функция RAG: находит релевантные чанки базы знаний сайта
    и формирует ответ модели строго на их основе.

    Возвращает {"answer": str, "sources": list[str]}.
    """
    matches = await retrieve_chunks(db, site_id, question)

    if not matches:
        return {"answer": NO_INFO_ANSWER, "sources": []}

    context = "\n\n---\n\n".join(
        f"Источник: {chunk.source_label}\n{chunk.content}" for chunk, _ in matches
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"КОНТЕКСТ:\n{context}\n\nВОПРОС: {question}"},
    ]

    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        temperature=0.2,  #
        max_tokens=800,   # ответ консультанта короткий; без лимита модель резервирует под макс. контекст,
                          
        extra_body={"usage": {"include": True}},  
    )
    log_chat_call("rag.answer_question", messages, response)

    answer_text = response.choices[0].message.content
    sources = list(dict.fromkeys(chunk.source_label for chunk, _ in matches))  # без дублей, с сохранением порядка

    return {"answer": answer_text, "sources": sources}