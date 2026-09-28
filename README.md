# Checko

Checko is a Telegram Mini App for automated receipt processing. It recognizes receipts with OCR, uses a large language model to extract and categorize expenses, and checks whether each expense qualifies for a tax deduction.

## Features

- **Receipt recognition.** Tesseract OCR with Russian and English language support.
- **Input formats.** JPG, PNG, PDF, WebP, HEIC, HEIF, AVIF.
- **Structured data extraction.** Receipt fields are extracted by an LLM through the OpenRouter API.
- **Expense categorization.** Each receipt is classified by expense type.
- **Tax deduction check.** Flags expenses that may be eligible for a tax deduction.
- **Document generation.** Produces ready-to-send letter templates for accounting.
- **Semantic search.** Search over a user's receipts using sentence-transformers embeddings.
- **Per-user isolation.** Each user has access only to their own receipts.

## Usage

1. Open the bot in Telegram and send `/start`.
2. Choose **Open Checko** to launch the Mini App (or **Contact support**).
3. Upload a photo or file of a receipt.
4. Processing takes about 30 seconds; results appear in the app once it is complete.

## Project structure

```
raif_task/
├── backend/          # Python / FastAPI
│   ├── app/          # Application code
│   └── prompts/      # LLM prompts
├── frontend/         # React / Vite / Tailwind CSS
│   └── src/
├── deploy/           # Production configuration
└── docker-compose.yml
```

## API

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `POST` | `/api/upload` | Upload a receipt (requires Telegram authentication) |
| `GET`  | `/api/list` | List the current user's receipts |
| `GET`  | `/api/search?q=...` | Search the current user's receipts |
| `GET`  | `/api/process/{id}` | Get processing status |
| `POST` | `/api/generate-template/{id}` | Generate a letter template |

Interactive API documentation is available at `http://localhost:8000/docs` when the backend is running.

## Configuration

Copy `.env.example` to `.env` and set the following variables:

```env
TELEGRAM_BOT_TOKEN=...                      # Issued by @BotFather
WEBAPP_URL=https://yourdomain.com           # Public HTTPS URL of the Mini App
OPENROUTER_API_KEY=...                      # From openrouter.ai
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
SECRET_TOKEN=...                            # Random string
```

## Running locally

```bash
cp .env.example .env    # then fill in the values
docker-compose up --build
```

## Production deployment

Requirements: a VPS running Ubuntu 22.04 with at least 2 GB of RAM, and a domain with an A record pointing to the server. HTTPS is required for Telegram Mini Apps.

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone and configure
git clone https://github.com/carevvv/raif_task.git
cd raif_task
cp .env.example .env    # set WEBAPP_URL to your domain

# Start the services
docker-compose -f docker-compose.prod.yml up -d --build

# Issue a TLS certificate
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

The bot starts automatically inside its container.

## Tech stack

- **Backend:** Python 3.11, FastAPI, Tesseract OCR, OpenRouter API, sentence-transformers, SQLite, python-telegram-bot
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Telegram WebApp API
- **Infrastructure:** Docker, Docker Compose, Nginx, Certbot

## License

Released under the [MIT License](LICENSE).
