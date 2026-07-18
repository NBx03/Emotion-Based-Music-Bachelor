# Emotion Music Generator (Дипломный проект)

[![backend-ci](https://github.com/NBx03/Emotion-Based-Music-Bachelor/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/NBx03/Emotion-Based-Music-Bachelor/actions/workflows/backend-ci.yml)

Веб-сервис для генерации персональных мелодий на основе анализа эмоционального содержания изображений.  
Проект состоит из **бэкенда** (Python + FastAPI + TensorFlow/CLIP + SunoAI API) и **фронтенда** (React.js).

## 📂 Структура проекта
- **backend/** — серверная часть: анализ изображений, генерация промптов и интеграция с API SunoAI.
- **frontend/** — клиентская часть: веб-интерфейс для загрузки изображений и воспроизведения музыки.

## 🚀 Основные возможности
- Анализ изображений с помощью модели CLIP, сопоставленной с центроидами эмоций датасета **EmoSet**.
- Выделение эмоциональных категорий и перцептивных признаков (яркость, насыщенность, лица, объекты).
- Формирование текстового запроса (промпта) для генерации музыки.
- Отправка запроса во внешний API (**SunoAI**) и получение готовых мелодий.
- Веб-интерфейс для загрузки изображений, выбора стиля и прослушивания треков.

> Полный датасет EmoSet для обычного запуска **не требуется**: backend
> использует предподсчитанные центроиды эмоций
> (`backend/data/emoset_centroids.json`). Датасет нужен только для того,
> чтобы пересчитать эти центроиды самостоятельно — см. раздел
> [Предподсчёт центроидов EmoSet](#-предподсчёт-центроидов-emoset).

## 🛠️ Используемые технологии
- **Backend**: Python, FastAPI, SQLAlchemy, TensorFlow, CLIP, SunoAI API
- **Frontend**: React.js, Axios, HTML/CSS/JS
- **Прочее**: REST API, SQLite (по умолчанию), Docker (опционально)

---

## ⚙️ Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/NBx03/Emotion-Based-Music-Bachelor.git
cd Emotion-Based-Music-Bachelor
````

### 2. Запуск бэкенда

Перейдите в папку `backend/`:

```bash
cd backend
```

Создайте виртуальное окружение и установите зависимости:

```bash
python3 -m venv venv
source venv/bin/activate   # для Linux/Mac
venv\Scripts\activate      # для Windows

pip install -r requirements.txt
```

Скопируйте файл с переменными окружения и заполните `SUNO_TOKEN`:

```bash
cp .env.example .env
# затем откройте .env и укажите свой SUNO_TOKEN
```

- `SUNO_TOKEN` — **обязателен**, сервер не запустится без него (API-ключ SunoAI).
- `DATABASE_URL` — опционален. Если не задан, backend по умолчанию использует
  локальный SQLite-файл `app.db` в папке `backend/`. Postgres подключается
  явно, например `postgresql://postgres:postgres@localhost:5432/postgres`.

Запустите сервер:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Бэкенд будет доступен по адресу: [http://localhost:8080](http://localhost:8080)
Документация FastAPI доступна по адресу: [http://localhost:8080/docs](http://localhost:8080/docs)

---

### 3. Запуск фронтенда

Перейдите в папку `frontend/`:

```bash
cd frontend
```

Установите зависимости:

```bash
npm install
```

Запустите dev-сервер:

```bash
npm start
```

Фронтенд будет доступен по адресу: [http://localhost:3000](http://localhost:3000)

---

### 4. Docker (опционально)

Можно запустить проект в контейнерах (нужен экспортированный `SUNO_TOKEN`):

```bash
export SUNO_TOKEN="your_suno_api_key"
docker-compose up --build
```

---

## ✅ Тесты

```bash
cd backend
pip install -r requirements-test.txt   # лёгкий набор, без torch/transformers/face_recognition
pytest tests/ -v
```

Smoke-тест на `POST /api/upload` подменяет `image_analysis.analyze_image`
до импорта `main.py`, поэтому не требует установки тяжёлых ML-зависимостей
и не делает реальных вызовов CLIP/YOLO/face_recognition. Прогоняется в CI
на каждый push/PR, затрагивающий `backend/` (см.
[.github/workflows/backend-ci.yml](.github/workflows/backend-ci.yml)).

---

## 🧠 Предподсчёт центроидов EmoSet

Backend сопоставляет CLIP-эмбеддинг загруженного изображения с центроидами
эмоций, предподсчитанными по датасету EmoSet и сохранёнными в
`backend/data/emoset_centroids.json`. Для обычного запуска сервиса сам
датасет EmoSet не нужен.

Если вы хотите пересчитать центроиды заново (например, на обновлённой
версии датасета), запустите скрипт там, где физически лежит EmoSet:

```bash
python scripts/precompute_centroids.py \
    --image-path /path/to/EmoSet/image \
    --annotation-path /path/to/EmoSet/annotation \
    --output backend/data/emoset_centroids.json
```

Подробности — в [backend/data/README.md](backend/data/README.md).

---

## 📸 Примеры

В `backend/examples/` лежит несколько тестовых изображений для ручной
проверки `/api/upload` без необходимости искать свои фото.

---

## 📖 О проекте

Данный репозиторий является реализацией моей выпускной квалификационной работы в НГУ ФИТ.
Цель проекта — разработка мультимодального веб-сервиса, который анализирует эмоциональное содержание изображений и генерирует соответствующие музыкальные мелодии.

## 📄 Лицензия

Проект распространяется под лицензией [MIT](LICENSE).
