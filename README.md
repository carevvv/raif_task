# 🧾 Checko - Обработка чеков с AI

Telegram Mini App для автоматического распознавания и обработки чеков.

## ✨ Возможности

- 📸 **Распознавание чеков** - Tesseract OCR с поддержкой русского и английского языков
- 🤖 **AI обработка** - Автоматическое извлечение данных через OpenRouter API
- 📊 **Категоризация расходов** - Классификация чеков по типам
- 💰 **Налоговые вычеты** - Проверка возможности получения вычета
- ✉️ **Генерация писем** - Готовые шаблоны для бухгалтерии
- 📱 **Telegram Mini App** - Удобный интерфейс прямо в мессенджере

## 🚀 Быстрый старт

### Требования:
- Docker и Docker Compose
- Telegram Bot Token ([получить у @BotFather](https://t.me/BotFather))
- OpenRouter API Key ([получить](https://openrouter.ai/keys))
- ngrok для локального тестирования ([скачать](https://ngrok.com/download))

### Локальный запуск (для тестирования):

```bash
# 1. Клонировать проект
git clone <your-repo>
cd raif_task

# 2. Создать .env файл
cp .env.example .env

# 3. Заполнить .env:
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENROUTER_API_KEY=your_openrouter_key_here
WEBAPP_URL=https://your-ngrok-url.ngrok-free.app  # Обновим позже

# 4. Запустить Docker
docker-compose up -d

# 5. Запустить ngrok (в отдельном терминале)
ngrok http 3000

# 6. Скопировать HTTPS URL из ngrok и обновить в .env:
WEBAPP_URL=https://abc-123-xyz.ngrok-free.app

# 7. Перезапустить backend
docker-compose restart backend

# 8. Запустить бота (в отдельном терминале)
cd backend
python -m app.telebot
```

### Использование:

1. Открыть Telegram и найти своего бота
2. Отправить `/start` - появятся кнопки:
   - 📱 **Открыть Checko** - запустить Mini App
   - 💬 **Написать в поддержку** - связаться с разработчиком
3. Загрузить фото чека
4. Получить уведомление об успешной загрузке
5. Дождаться обработки (~30 секунд)
6. Посмотреть результаты

## Структура

```
raif_task/
├── backend/          # Python/FastAPI
│   ├── app/          # Код приложения
│   └── prompts/      # Промпты для AI
├── frontend/         # React/Vite/Tailwind
│   └── src/          # Исходный код
├── deploy/           # Конфиги для production
└── docker-compose.yml
```

## API

- `POST /api/upload` - Загрузить чек
- `GET /api/list` - Список чеков
- `GET /api/search?q=...` - Поиск
- `GET /api/process/{id}` - Статус обработки
- `POST /api/generate-template/{id}` - Сгенерировать письмо

Документация: http://localhost:8000/docs

## 🌐 Production Deploy

### Подготовка:
1. **VPS сервер** - Ubuntu 22.04, минимум 2GB RAM
2. **Домен** - для HTTPS (требуется для Mini App)
3. **DNS настройка** - A-запись домена на IP сервера

### Деплой на VPS:

```bash
# 1. На сервере установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Клонировать проект
git clone <your-repo>
cd raif_task

# 3. Настроить .env для продакшена
cp .env.example .env
nano .env

# Важно! WEBAPP_URL должен быть вашим доменом:
TELEGRAM_BOT_TOKEN=...
OPENROUTER_API_KEY=...
WEBAPP_URL=https://yourdomain.com
SECRET_TOKEN=... # Случайная строка для безопасности

# 4. Запустить в production режиме
docker-compose -f docker-compose.prod.yml up -d --build

# 5. Настроить SSL с Certbot
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com

# ✅ Готово Бот автоматически запустится в контейнере
```


## Переменные окружения

```env
TELEGRAM_BOT_TOKEN=...          # От @BotFather
WEBAPP_URL=https://yourdomain.com
OPENROUTER_API_KEY=...          # От openrouter.ai
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
SECRET_TOKEN=...                # Случайная строка
```


## 🔧 Технологии

### Backend:
- **Python 3.11** + **FastAPI** - быстрый и современный API
- **Tesseract OCR** - распознавание текста (режим PSM 3, OEM 1 для русского)
- **OpenRouter API** - LLM обработка (Mistral 7B по умолчанию)
- **sentence-transformers** - локальные embeddings (опционально)
- **SQLite** - простая и надежная БД
- **python-telegram-bot** - интеграция с Telegram

### Frontend:
- **React 18** + **TypeScript** - типобезопасный UI
- **Vite** - быстрая сборка
- **Tailwind CSS** - современные стили
- **Telegram WebApp API** - нативная интеграция с Mini App

### DevOps:
- **Docker** + **Docker Compose** - контейнеризация
- **Nginx** - production web-сервер
- **Certbot** - автоматический SSL


## 📄 Лицензия - MIT License