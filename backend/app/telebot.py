"""
Telegram Bot integration for Checko.
Simple bot that sends a button to open the Web App.
"""
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from app.config import settings
import structlog

logger = structlog.get_logger()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        f"Я помогу тебе обрабатывать чеки и документы.\n\n"
        f"Используй /open чтобы открыть приложение.",
    )


async def open_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /open command - send button to open Web App."""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🧾 Открыть Checko",
                web_app=WebAppInfo(url=settings.WEBAPP_URL)
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Нажми кнопку ниже, чтобы открыть приложение:",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """
🧾 *Checko - Помощник по обработке чеков*

Доступные команды:
/start - Начать работу с ботом
/open - Открыть веб-приложение
/help - Показать это сообщение

Что умеет приложение:
✅ Распознавать текст с чеков (OCR)
✅ Извлекать структурированные данные
✅ Классифицировать расходы
✅ Генерировать шаблоны писем
✅ Семантический поиск по чекам
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")


def run_bot():
    """Run the Telegram bot."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Bot cannot start.")
        return
    
    logger.info("Starting Telegram bot", webapp_url=settings.WEBAPP_URL)
    
    # Create application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("open", open_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Run the bot
    logger.info("Telegram bot is running")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_bot()
