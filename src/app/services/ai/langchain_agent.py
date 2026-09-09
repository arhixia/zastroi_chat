import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.settings.config import settings

logger = logging.getLogger("langchain_agent")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(name)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

examples = [
    {
        "input": "Сколько стоит двушка?",
        "output": {
            "answer": "Стоимость двухкомнатных квартир начинается от 5.2 млн рублей.\n\n📞 Оставьте свои контакты, и менеджер подберет точную планировку!",
            "ask_lead": True
        }
    },
    {
        "input": "Привет",
        "output": {
            "answer": "Здравствуйте! Я помощник застройщика. Чем могу помочь?\n\n💬 Если у вас есть конкретные вопросы по ценам или ипотеке — спрашивайте, или оставьте номер для связи.",
            "ask_lead": False
        }
    },
    {
        "input": "Как написать алгоритм сортировки?",
        "output": {
            "answer": "Извините, я могу отвечать только на вопросы, связанные с недвижимостью, квартирами и жилищными комплексами. Пожалуйста, задайте вопрос по нашей теме.",
            "ask_lead": False
        }
    },
    {
        "input": "Что такое Python?",
        "output": {
            "answer": "Извините, я специализируюсь только на вопросах по недвижимости. Если у вас есть вопросы о наших квартирах, ценах или условиях покупки — с удовольствием отвечу!",
            "ask_lead": False
        }
    }
]

example_prompt = ChatPromptTemplate.from_messages(
    [("human", "{input}"), ("ai", "{output}")]
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

final_prompt = ChatPromptTemplate.from_messages([
    ("system", """Ты — эксперт по продажам недвижимости. Твоя задача — помогать клиентам с вопросами о квартирах, домах и жилищных комплексах.

ОГРАНИЧЕНИЯ:
- Отвечай ТОЛЬКО на вопросы, связанные с недвижимостью (цены, ипотека, планировки, этажи, паркинг, район, инфраструктура ЖК, условия покупки и т.д.)
- Если вопрос НЕ относится к недвижимости (программирование, алгоритмы, математика, история, кулинария и другие темы), вежливо откажись отвечать и предложи задать вопрос по недвижимости

ПРАВИЛА ОТВЕТОВ:
1. Отвечай кратко и дружелюбно на основе КОНТЕКСТА.
2. Если вопрос про ЦЕНУ, ИПОТЕКУ или ПОКУПКУ — в конце ответа добавь призыв оставить контакты.
3. Если вопрос простой (про паркинг, этаж) — отвечай фактом, без навязчивого призыва.
4. Если информации нет — честно скажи об этом и предложи оставить контакты. Но иногда все же пытайся предложить оставить контакт

ВАЖНО: Отвечай СТРОГО в формате JSON:
- 'answer': строка с ответом.
- 'ask_lead': boolean (true ТОЛЬКО если ты хочешь, чтобы появилась форма заявки).

Контекст: {context}"""),
    few_shot_prompt,
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

async def get_smart_response(question: str, context: str = ""):
    try:
        logger.info(f"Запрос к LangChain: '{question}'")
        result = await chain.ainvoke({"question": question, "context": context})
        logger.info(f"Ответ LangChain: {result}")
        return result
    except Exception as e:
        logger.error(f"[LangChain Error]: {e}")
        return {"answer": "Произошла техническая ошибка.", "ask_lead": False}