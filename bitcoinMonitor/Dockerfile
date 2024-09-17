# Базовый образ, используем Python
FROM python:3.9-slim

# Установка рабочей директории в контейнере
WORKDIR /app

# Копирование requirements.txt в рабочую директорию
COPY requirments.txt .

# Установка зависимостей из requirements.txt
RUN pip install --no-cache-dir -r requirments.txt

# Копирование всех файлов проекта в контейнер
COPY . .

# Открытие порта для взаимодействия с API (если это необходимо)
EXPOSE 587

# Команда по умолчанию для запуска вашего приложения
CMD ["python", "task_meneger.py"]
