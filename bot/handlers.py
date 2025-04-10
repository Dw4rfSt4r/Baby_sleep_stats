import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from bot.database import init_db, save_session, get_sessions_for_user
from bot.utils import generate_excel_and_chart
from datetime import datetime
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Текущее состояние сна
current_session = {}

def start_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_comments))

    init_db()
    print("Бот запущен...")
    app.run_polling()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Начать сон", callback_data="start_sleep"),
            InlineKeyboardButton("Закончить сон", callback_data="end_sleep"),
        ],
        [InlineKeyboardButton("Получить статистику", callback_data="get_stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "start_sleep":
        current_session[user_id] = {"start_time": datetime.now()}
        await query.edit_message_text("Сон начат. Добавьте комментарий (если нужно):")
    elif query.data == "end_sleep":
        if user_id not in current_session or "start_time" not in current_session[user_id]:
            await query.edit_message_text("Сначала начните сон!")
        else:
            session = current_session[user_id]
            session["end_time"] = datetime.now()
            session["duration"] = (session["end_time"] - session["start_time"]).total_seconds() / 3600
            save_session(user_id, session)
            await query.edit_message_text("Сон завершён. Добавьте комментарий (если нужно):")
    elif query.data == "get_stats":
        sessions = get_sessions_for_user(user_id)
        if not sessions:
            await query.edit_message_text("Нет данных для отображения статистики.")
        else:
            file_path, chart_path = generate_excel_and_chart(sessions)
            await query.message.reply_document(open(file_path, "rb"))
            await query.message.reply_photo(open(chart_path, "rb"))

async def handle_comments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id in current_session and "end_time" not in current_session[user_id]:
        current_session[user_id]["start_comment"] = text
        await update.message.reply_text("Комментарий к началу сна сохранён.")
    elif user_id in current_session and "end_time" in current_session[user_id]:
        current_session[user_id]["end_comment"] = text

        # Сохранение данных в базу
        session = current_session[user_id]
        save_session(user_id, session)
        await update.message.reply_text("Комментарий к окончанию сна сохранён.")
        del current_session[user_id]
    else:
        await update.message.reply_text("Непонятная команда. Используйте /start.")