from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from bot.utils import generate_excel_and_chart
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что файл .env содержит TELEGRAM_BOT_TOKEN=<ваш_токен>.")

# Глобальная переменная для хранения текущего состояния пользователя
user_state = {}

async def start(update: Update, context):
    """Обработчик команды /start. Показывает стартовое меню."""
    await show_main_menu(update)

async def handle_buttons(update: Update, context):
    """Обработчик кнопок."""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "start_sleep":
        user_state[user_id] = {"action": "start_sleep", "start_time": datetime.now()}
        keyboard = [
            [InlineKeyboardButton("Да", callback_data="add_start_comment")],
            [InlineKeyboardButton("Нет", callback_data="skip_start_comment")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Оставить комментарий?", reply_markup=reply_markup)

    elif query.data == "add_start_comment":
        user_state[user_id]["awaiting_comment"] = True
        await query.edit_message_text("Введите ваш комментарий:")

    elif query.data == "skip_start_comment":
        user_state[user_id]["start_comment"] = None
        await send_sleep_start_message(user_id, query)

    elif query.data == "end_sleep":
        if user_id in user_state and "start_time" in user_state[user_id]:
            user_state[user_id]["end_time"] = datetime.now()
            keyboard = [
                [InlineKeyboardButton("Да", callback_data="add_end_comment")],
                [InlineKeyboardButton("Нет", callback_data="skip_end_comment")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Оставить комментарий к окончанию сна?", reply_markup=reply_markup)
        else:
            await query.edit_message_text("Вы еще не начали сон. Пожалуйста, выберите 'Начать сон'.")

    elif query.data == "add_end_comment":
        user_state[user_id]["awaiting_comment"] = True
        user_state[user_id]["action"] = "add_end_comment"
        await query.edit_message_text("Введите ваш комментарий к окончанию сна:")

    elif query.data == "skip_end_comment":
        user_state[user_id]["end_comment"] = None
        await send_sleep_end_message(user_id, query)

    elif query.data == "current_sleep_duration":
        if user_id in user_state and "start_time" in user_state[user_id]:
            duration = datetime.now() - user_state[user_id]["start_time"]
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes = remainder // 60
            await query.edit_message_text(f"С момента начала сна прошло: {int(hours)}ч {int(minutes)}м.")
        else:
            await query.edit_message_text("Сон еще не начат.")
        await show_main_menu(query)

    elif query.data == "time_since_last_sleep":
        if "last_sleep_end" in user_state.get(user_id, {}):
            duration = datetime.now() - user_state[user_id]["last_sleep_end"]
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes = remainder // 60
            await query.edit_message_text(f"С момента завершения последнего сна прошло: {int(hours)}ч {int(minutes)}м.")
        else:
            await query.edit_message_text("Данные о последнем сне отсутствуют.")
        await show_main_menu(query)

    elif query.data == "get_stats":
        from bot.database import get_sessions_for_user
        sessions = get_sessions_for_user(user_id)
        if not sessions:
            await query.edit_message_text("Нет данных для отображения статистики.")
        else:
            file_path, chart_path = generate_excel_and_chart(sessions)
            await query.message.reply_document(open(file_path, "rb"))
            await query.message.reply_photo(open(chart_path, "rb"))
            await show_main_menu(query.message)

async def handle_message(update: Update, context):
    """Обработчик текстовых сообщений."""
    user_id = update.message.from_user.id

    if user_id in user_state and user_state[user_id].get("awaiting_comment"):
        action = user_state[user_id]["action"]
        if action == "start_sleep":
            user_state[user_id]["start_comment"] = update.message.text
            await send_sleep_start_message(user_id, update.message)
        elif action == "add_end_comment":
            user_state[user_id]["end_comment"] = update.message.text
            await send_sleep_end_message(user_id, update.message)

async def send_sleep_start_message(user_id, message_or_query):
    """Отправляет сообщение о начале сна и возвращает в меню."""
    start_time = user_state[user_id]["start_time"].strftime("%H:%M:%S")
    if "awaiting_comment" in user_state[user_id]:
        del user_state[user_id]["awaiting_comment"]

    # Отправляем сообщение в зависимости от типа объекта
    if isinstance(message_or_query, Update) and message_or_query.message:
        await message_or_query.message.reply_text(f"Сон начат в {start_time}.")
    elif hasattr(message_or_query, "message") and message_or_query.message:
        await message_or_query.message.reply_text(f"Сон начат в {start_time}.")
    
    await show_main_menu(message_or_query)

async def send_sleep_end_message(user_id, message_or_query):
    """Отправляет сообщение о завершении сна и возвращает в меню."""
    user_state[user_id]["last_sleep_end"] = user_state[user_id]["end_time"]
    end_time = user_state[user_id]["end_time"].strftime("%H:%M:%S")
    if "awaiting_comment" in user_state[user_id]:
        del user_state[user_id]["awaiting_comment"]

    # Отправляем сообщение в зависимости от типа объекта
    if isinstance(message_or_query, Update) and message_or_query.message:
        await message_or_query.message.reply_text(f"Сон завершен в {end_time}.")
    elif hasattr(message_or_query, "message") and message_or_query.message:
        await message_or_query.message.reply_text(f"Сон завершен в {end_time}.")
    
    await save_sleep_session(user_id, message_or_query)
    await show_main_menu(message_or_query)

async def save_sleep_session(user_id, message_or_query):
    """Сохраняет данные о сеансе сна в базу."""
    from bot.database import save_session
    start_time = user_state[user_id]["start_time"]
    end_time = user_state[user_id]["end_time"]
    duration = (end_time - start_time).total_seconds() / 3600
    start_comment = user_state[user_id].get("start_comment")
    end_comment = user_state[user_id].get("end_comment")

    session = {
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
        "start_comment": start_comment,
        "end_comment": end_comment,
    }
    save_session(user_id, session)

    del user_state[user_id]["start_time"]
    del user_state[user_id]["end_time"]

async def show_main_menu(update_or_query):
    """Показывает главное меню."""
    keyboard = [
        [InlineKeyboardButton("Начать сон", callback_data="start_sleep")],
        [InlineKeyboardButton("Закончить сон", callback_data="end_sleep")],
        [InlineKeyboardButton("Текущая длительность сна", callback_data="current_sleep_duration")],
        [InlineKeyboardButton("Время с последнего сна", callback_data="time_since_last_sleep")],
        [InlineKeyboardButton("Получить статистику", callback_data="get_stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text("Выберите действие:", reply_markup=reply_markup)
    elif hasattr(update_or_query, "edit_message_text"):
        await update_or_query.edit_message_text("Выберите действие:", reply_markup=reply_markup)

def register_handlers(dispatcher):
    """Регистрирует обработчики."""
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(handle_buttons))
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

def start_bot():
    """Запускает бота."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    register_handlers(application)
    application.run_polling()