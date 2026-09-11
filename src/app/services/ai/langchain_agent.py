import logging
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from app.services.ai.examples import examples
from app.settings.config import settings

logger = logging.getLogger("langchain_agent")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(name)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


example_prompt = ChatPromptTemplate.from_messages(
    [("human", "{input}"), ("ai", "{output}")]
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

final_prompt = ChatPromptTemplate.from_messages([
    ("system", """Ты — эксперт по продажам недвижимости. Твоя задача — помогать клиентам с вопросами о квартирах, домах и жилищных комплексах.

ТЕКУЩИЙ СЧЕТЧИК СООБЩЕНИЙ КЛИЕНТА: {message_count}

ВАЖНО ПРО КОНТЕКСТ ДИАЛОГА:
- Ниже, после примеров формата (few-shot), тебе передаётся РЕАЛЬНАЯ история текущего диалога (chat_history).
- Используй её, чтобы понимать местоимения и отсылки к прошлым сообщениям («там», «а про него», «эту квартиру» и т.п.) — определяй, о каком именно ЖК или объекте идёт речь, по последним репликам.
- Примеры (few-shot) НИЖЕ — это ТОЛЬКО образцы формата ответа. Названия ЖК и цифры из них ("Южный полюс" и т.д.) — вымышленные для примера. НИКОГДА не используй их как реальные факты и не подставляй их в ответ, если пользователь сам их не называл.

ОГРАНИЧЕНИЯ:
- Отвечай ТОЛЬКО на вопросы, связанные с недвижимостью. Если вопрос не по теме (программирование, рецепты и т.д.), вежливо откажись.

ПРАВИЛА ОТВЕТОВ:
1. Отвечай кратко, дружелюбно и только на основе КОНТЕКСТА.
2. ПРАВИЛО ЛИДОГЕНЕРАЦИИ:
   Ставь "ask_lead": true и добавляй призыв оставить контакты, если верно ЛЮБОЕ из условий:
   а) message_count кратен 3 (3-е, 6-е, 9-е сообщение и т.д.);
   б) клиент сам прямо спросил про покупку, бронь или оформление;
   в) вопрос ПО ТЕМЕ недвижимости, но в КОНТЕКСТЕ нет данных для ответа на конкретный запрос — в этом случае вежливо сообщи, что не располагаешь этой конкретной информацией, и предложи оставить контакты.
   Если НЕ подходит ни под один из пунктов (а), (б), (в) — **КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО** просить контакты и ставить "ask_lead": true.
3. Призыв к действию пиши с новой строки через двойной перенос (\\n\\n).

ВАЖНО: Отвечай СТРОГО в формате JSON:
- 'answer': строка с ответом.
- 'ask_lead': boolean.

Контекст: {context}"""),
    few_shot_prompt,
    MessagesPlaceholder("chat_history"),
    ("human", "{question}")
])


model = ChatOpenAI(
    openai_api_key=settings.OPENROUTER_API_KEY,
    openai_api_base=settings.OPENROUTER_BASE_URL, 
    model_name=settings.LLM_MODEL,
    temperature=0.2,
    model_kwargs={"response_format": {"type": "json_object"}}
)

chain = final_prompt | model | JsonOutputParser()


def _build_chat_history(history):
    messages = []
    for msg in history or []:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    return messages


async def get_smart_response(question: str, context: str = "", message_count: int = 1, history: list | None = None):
    try:
        logger.info(f"Запрос к LangChain [{message_count}]: '{question}'")
        chat_history = _build_chat_history(history)
        result = await chain.ainvoke({
            "question": question, 
            "context": context, 
            "message_count": message_count,
            "chat_history": chat_history,
        })
        logger.info(f"Ответ LangChain: {result}")
        return result
    except Exception as e:
        logger.error(f"[LangChain Error]: {e}")
        return {"answer": "Произошла техническая ошибка.", "ask_lead": False}