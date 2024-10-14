# Используем базовый образ Python (можно slim, но с установкой нужных зависимостей)
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем необходимые системные зависимости для сборки psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Обновляем pip до последней версии
RUN pip install --upgrade pip

# Копируем requirements.txt и устанавливаем все зависимости (без psycopg2-binary)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем psycopg2 отдельно
RUN pip install psycopg2

# Копируем остальные файлы приложения
COPY . .

# Открываем порт 5000 для доступа к приложению
EXPOSE 5000

# Запуск приложения через Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
