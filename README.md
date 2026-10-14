# 1. Создать .env и заполнить DB_PASS, OPENROUTER_API_KEY, JWT_SECRET, API_HOST, WIDGET_SCRIPT_URL
cp .env.example .env

# 2. Запустить
docker compose up -d --build

# 3. Создать админа
docker compose exec api sh -c "cd src && python scripts/create_admin.py <username> <password>"


# Пример добавления сайта в админке:

Название
test123

Домен (без http:// !!)

test-builder-site

Стартовые URL

http://test-builder-site/index.html

По одному URL на строку или через запятую

Исключить URL

/infrastructure


# Добавление виджета

После создания сайта будет кнопка Код виджета 

Пример: <script src="http://localhost:8000/widget.js" data-site-id="d5a90a0a-0c3b-4a87-b1a7-8449cb6f7a6f" async></script>

Эту строка надо вставить в index.html сайта 
