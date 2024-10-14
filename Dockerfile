# Используем официальный образ Python (легкий)
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Скопируем requirements.txt и установим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все остальные файлы в контейнер
COPY . .

# Открываем порт 5000 для доступа к приложению
EXPOSE 5000

# Запуск приложения через Gunicorn
# Используем правило CPU * 2 + 1 для количества воркеров
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
