FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание .env файла из примера (если не существует)
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Запуск бота
CMD ["python", "bot.py"]
