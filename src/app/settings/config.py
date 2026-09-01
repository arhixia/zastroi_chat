import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    ENV: str = os.getenv("ENV", "local")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")

    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    REDIS_URL: str = os.getenv("REDIS_URL")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

    #AI
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL")

    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-5.6-terra")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM"))

    #adminauth
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES"))

    WIDGET_SCRIPT_URL: str = os.getenv("WIDGET_SCRIPT_URL")

    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"


settings = Settings()