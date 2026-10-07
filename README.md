DEBUG=false                  # режим отладки FastAPI
SQL_ECHO=false               # логировать каждый SQL-запрос

DB_HOST=postgres             
DB_PORT=5432                
DB_NAME=postgres             
DB_USER=postgres             
DB_PASS=pass                    

###
# можно не менять (кроме OPENROUTER_API_KEY,JWT_SECRET)
REDIS_HOST=redis             # имя сервиса Redis

REDIS_PORT=6379              # порт Redis

REDIS_DB=0                   # номер БД Redis

OPENROUTER_API_KEY=  # ключ доступа к OpenRouter

OPENROUTER_BASE_URL=https://openrouter.ai/api/v1    # адрес API OpenRouter

LLM_MODEL=openai/gpt-5.6-terra                        # модель для генерации ответов

EMBEDDING_MODEL=openai/text-embedding-3-small        # модель для эмбеддингов 

EMBEDDING_DIM=1536                                     # размерность вектора этой модели

JWT_SECRET=  # секретный ключ подписи токенов авторизации

JWT_ALGORITHM=HS256          # алгоритм подписи JWT

JWT_EXPIRE_MINUTES=100       # сколько минут живёт токен авторизации
###

WIDGET_SCRIPT_URL=http://localhost:8000/widget.js    # публичный адрес, откуда грузится виджет

API_HOST=http://localhost:8000                          # публичный адрес самого API


# Затем

docker compose up -d --build

# Прокинуть админа в систему
docker compose exec api sh -c "cd src && python scripts/create_admin.py <username> <password>"