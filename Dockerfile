# Используем официальный образ Python (легкий)
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Установка системных зависимостей для сборки (необходимые для psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    build-essential \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Обновляем pip до последней версии
RUN pip install --upgrade pip

# Копируем requirements.txt и устанавливаем все зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем psycopg2-binary
RUN pip install psycopg2-binary

# Копируем все остальные файлы в контейнер
COPY . .

# Открываем порт 5000 для доступа к приложению
EXPOSE 5000

# Запуск приложения через Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
