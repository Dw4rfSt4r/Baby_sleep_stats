import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(__file__))

from bot.handlers import register_handlers
from telegram.ext import ApplicationBuilder
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что файл .env содержит TELEGRAM_BOT_TOKEN=<ваш_токен>.")

def main():
    """Точка входа в приложение."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    register_handlers(application)
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()