from . import bot_logic
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile

# Состояние для отслеживания добавления комментариев
user_states = {}

async def start(update, context):
    """Обработчик команды /start. Показывает стартовое меню."""
    await show_main_menu(update)

async def handle_buttons(update, context):
    """Обработчик кнопок."""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "start_sleep":
        message = bot_logic.start_sleep(user_id)
        user_states[user_id] = {"action": "start_comment"}
        await query.edit_message_text(message)
        await ask_for_comment(query)

    elif query.data == "end_sleep":
        message = bot_logic.end_sleep(user_id)
        user_states[user_id] = {"action": "end_comment"}
        await query.edit_message_text(message)
        await ask_for_comment(query)

    elif query.data == "add_comment_yes":
        # Убедимся, что user_id присутствует в user_states
        user_states.setdefault(user_id, {})
        user_states[user_id]["waiting_for_comment"] = True
        await query.edit_message_text("Введите ваш комментарий:")

    elif query.data == "add_comment_no":
        # Удаление состояния и возврат в главное меню
        user_states.pop(user_id, None)
        await show_main_menu(query)

    elif query.data == "current_sleep_duration":
        message = bot_logic.get_current_duration(user_id)
        await query.edit_message_text(message)
        await show_main_menu(query)

    elif query.data == "time_since_last_sleep":
        message = bot_logic.get_last_sleep_duration(user_id)
        await query.edit_message_text(message)
        await show_main_menu(query)

    elif query.data == "export_statistics":
        file_path = bot_logic.export_statistics_to_excel(user_id)
        if file_path:
            with open(file_path, "rb") as file:
                await query.message.reply_document(InputFile(file), caption="Ваша статистика сна.")
        else:
            await query.message.reply_text("Нет данных для выгрузки.")
        await show_main_menu(query)

async def handle_text(update, context):
    """Обработчик текстовых сообщений (например, для комментариев)."""
    user_id = update.message.from_user.id

    if user_id in user_states and user_states[user_id].get("waiting_for_comment"):
        comment = update.message.text
        action = user_states[user_id]["action"]

        if action == "start_comment":
            bot_logic.add_start_comment(user_id, comment)
        elif action == "end_comment":
            bot_logic.add_end_comment(user_id, comment)

        # Удаляем состояние пользователя и показываем меню
        user_states.pop(user_id, None)
        await update.message.reply_text("Комментарий добавлен.")
        await show_main_menu(update)

async def ask_for_comment(update_or_query, context=None):
    """Задает вопрос о добавлении комментария."""
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="add_comment_yes")],
        [InlineKeyboardButton("Нет", callback_data="add_comment_no")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text("Добавить комментарий?", reply_markup=reply_markup)
    elif hasattr(update_or_query, "edit_message_text"):
        await update_or_query.edit_message_text("Добавить комментарий?", reply_markup=reply_markup)

async def show_main_menu(update_or_query):
    """Показывает главное меню."""
    keyboard = [
        [InlineKeyboardButton("Начать сон", callback_data="start_sleep")],
        [InlineKeyboardButton("Закончить сон", callback_data="end_sleep")],
        [InlineKeyboardButton("Текущая длительность сна", callback_data="current_sleep_duration")],
        [InlineKeyboardButton("Время с последнего сна", callback_data="time_since_last_sleep")],
        [InlineKeyboardButton("Выгрузить статистику", callback_data="export_statistics")],  # Новая кнопка
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
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))