FROM python:3.9-slim

# Обновляем список пакетов и устанавливаем CMake, build-essential и другие зависимости
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libgtk-3-dev \
    libboost-python-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект в рабочую директорию
COPY . .

# Запускаем приложение с помощью uvicorn на порту 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
