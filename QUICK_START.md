# 🚀 Checko - Быстрый старт

## За 3 минуты

### 1. Получить API ключи

**Telegram Bot**:
- Открыть https://t.me/BotFather
- Команда: `/newbot`
- Следовать инструкциям
- Скопировать токен

**OpenRouter**:
- Регистрация: https://openrouter.ai/
- Перейти: https://openrouter.ai/keys
- Создать новый ключ
- Скопировать `sk-or-v1-...`

### 2. Установить

```bash
git clone <your-repo>
cd raif_task
cp .env.example .env
```

### 3. Настроить .env

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...  # От BotFather
OPENROUTER_API_KEY=sk-or-v1-...      # От OpenRouter
WEBAPP_URL=http://localhost:3000
SECRET_TOKEN=your-random-string
```

### 4. Запустить

```bash
docker-compose up --build
```

### 5. Использовать

1. Открыть Telegram → найти своего бота
2. Отправить `/open`
3. Нажать "Открыть Checko"
4. Загрузить фото чека
5. Готово!

## Без Docker

### Backend

```bash
cd backend

# Установить Tesseract
# Ubuntu:
sudo apt-get install tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng

# macOS:
brew install tesseract tesseract-lang

# Запустить
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Production

```bash
# На сервере Ubuntu
./deploy/setup.sh
cp .env.example .env
nano .env  # Настроить

# SSL
./deploy/ssl_setup.sh yourdomain.com

# Запустить
docker-compose -f docker-compose.prod.yml up -d
```

## Готово! 🎉

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
