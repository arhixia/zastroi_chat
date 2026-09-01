FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Системные библиотеки под Chromium ставим вручную, актуальными для Debian
# bookworm именами. НЕ используем "playwright install --with-deps" — этот
# флаг тянет пакеты по старым именам (ttf-ubuntu-font-family, ttf-unifont),
# которых в bookworm больше нет (переименованы в fonts-*), и падает с ошибкой
# "has no installation candidate". См. github.com/microsoft/playwright/issues/24028
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libdbus-1-3 libxcb1 libxkbcommon0 libx11-6 libxcomposite1 libxdamage1 \
    libxext6 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
    libasound2 libatspi2.0-0 libgtk-3-0 \
    fonts-liberation fonts-unifont \
    ca-certificates wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt \
    && playwright install chromium

COPY src ./src
COPY migrations ./migrations
COPY alembic.ini .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]