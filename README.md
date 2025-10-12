# 🧾 Checko - Обработка чеков с AI

Telegram Mini App для автоматического распознавания и обработки чеков.

## Возможности

- 📸 **Распознавание чеков** - Tesseract OCR с поддержкой русского и английского языков
- 🖼️ **Поддержка форматов** - JPG, PNG, PDF, WebP, HEIC, HEIF, AVIF
- 🤖 **AI обработка** - Автоматическое извлечение данных через OpenRouter API
- 📊 **Категоризация расходов** - Классификация чеков по типам
- 💰 **Налоговые вычеты** - Проверка возможности получения вычета
- ✉️ **Генерация писем** - Готовые шаблоны для бухгалтерии
- 📱 **Telegram Mini App** - Удобный интерфейс прямо в мессенджере
- 🔒 **Приватность** - Каждый пользователь видит только свои чеки


### Использование:

1. Открыть Telegram и найти своего бота
2. Отправить `/start` - появятся кнопки:
   - **Открыть Checko** - запустить Mini App
   - **Написать в поддержку** - связаться с разработчиком
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

- `POST /api/upload` - Загрузить чек (требует Telegram auth)
- `GET /api/list` - Список чеков пользователя
- `GET /api/search?q=...` - Поиск по чекам пользователя
- `GET /api/process/{id}` - Статус обработки
- `POST /api/generate-template/{id}` - Сгенерировать письмо

Документация: http://localhost:8000/docs

##  Production Deploy

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

# WEBAPP_URL должен быть вашим доменом:
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
- **Python 3.11** + **FastAPI**
- **Tesseract OCR**
- **OpenRouter API**
- **sentence-transformers** 
- **SQLite** 
- **python-telegram-bot**

### Frontend:
- **React 18** + **TypeScript**
- **Vite**
- **Tailwind CSS** 
- **Telegram WebApp API** 

### DevOps:
- **Docker** + **Docker Compose**
- **Nginx** 
- **Certbot**


## 📄 Лицензия - MIT License