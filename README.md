# 🧾 Checko - Простая обработка чеков с AI

Демо-система для распознавания и обработки чеков через Telegram Mini App.

## Что это?

**Checko** - это простой инструмент который:
- 📸 Распознаёт текст с фото чеков (OCR)
- 🤖 Извлекает данные через AI (OpenRouter)
- 📁 Классифицирует расходы
- ✉️ Генерирует письма в бухгалтерию
- 🔍 Ищет чеки по смыслу

## Быстрый старт (3 минуты)

### Что нужно:
1. Docker и Docker Compose
2. Telegram Bot Token ([получить](https://t.me/BotFather))
3. OpenRouter API Key ([получить](https://openrouter.ai/keys))

### Запуск:

```bash
# 1. Клонировать
git clone <your-repo>
cd raif_task

# 2. Настроить
cp .env.example .env
nano .env  # Добавить TELEGRAM_BOT_TOKEN и OPENROUTER_API_KEY

# 3. Запустить
docker-compose up --build

# ✅ Готово!
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Как пользоваться:

1. Открыть Telegram → найти своего бота
2. Отправить `/open`
3. Нажать кнопку "Открыть Checko"
4. Загрузить фото чека
5. Дождаться обработки
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

## Production Deploy

```bash
# На Ubuntu VPS:
./deploy/setup.sh
cp .env.example .env
nano .env  # Настроить
./deploy/ssl_setup.sh yourdomain.com
docker-compose -f docker-compose.prod.yml up -d
```

## Переменные окружения

```env
TELEGRAM_BOT_TOKEN=...          # От @BotFather
WEBAPP_URL=https://yourdomain.com
OPENROUTER_API_KEY=...          # От openrouter.ai
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
SECRET_TOKEN=...                # Случайная строка
```

## Troubleshooting

```bash
# Логи
docker-compose logs -f

# Перезапуск
docker-compose restart

# Полная очистка
docker-compose down
rm backend/checko.db
docker-compose up --build
```

## Технологии

- **Backend**: Python 3.11, FastAPI, Tesseract OCR
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **AI**: OpenRouter API
- **Embeddings**: sentence-transformers (локально)
- **DB**: SQLite
- **Deploy**: Docker, Nginx

## Лицензия - MIT