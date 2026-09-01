from openai import AsyncOpenAI
 
from app.settings.config import settings


client = AsyncOpenAI(
    base_url=settings.OPENROUTER_BASE_URL,
    api_key=settings.OPENROUTER_API_KEY
)