from . import bot_logic
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
from datetime import datetime

# Состояние для отслеживания действий пользователей
user_states = {}

async def start(update, context):
    """Обработчик команды /start. Показывает главное меню."""
    await show_main_menu(update)

async def handle_buttons(update, context):
    """Обработчик кнопок."""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "start_sleep":
        message = bot_logic.start_sleep(user_id)
        user_states[user_id] = {"action": "start_comment"}
        await query.message.reply_text(message)
        await ask_for_comment(query.message)

    elif query.data == "end_sleep":
        message = bot_logic.end_sleep(user_id)
        user_states[user_id] = {"action": "end_comment"}
        await query.message.reply_text(message)
        await ask_for_comment(query.message)

    elif query.data == "current_sleep_duration":
        message = bot_logic.get_current_duration(user_id)
        await query.message.reply_text(message)

    elif query.data == "time_since_last_sleep":
        message = bot_logic.get_last_sleep_duration(user_id)
        await query.message.reply_text(message)

    elif query.data == "add_missed_sleep":
        await query.message.reply_text("Введите данные о пропущенном сне в формате:\n\n"
                                       "Начало: dd.mm.yyyy HH:MM\nКонец: dd.mm.yyyy HH:MM")
        user_states[user_id] = {"action": "missed_sleep"}

    elif query.data == "daily_statistics":
        stats = bot_logic.generate_daily_statistics(user_id)
        await query.message.reply_text(stats)

async def handle_text(update, context):
    """Обработчик текстовых сообщений."""
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "Главное меню":
        # При нажатии на кнопку "Главное меню"
        await show_main_menu(update)
        return

    if text == "Начать сон":
        message = bot_logic.start_sleep(user_id)
        user_states[user_id] = {"action": "start_comment"}
        await update.message.reply_text(message)
        await ask_for_comment(update.message)

    elif text == "Закончить сон":
        message = bot_logic.end_sleep(user_id)
        user_states[user_id] = {"action": "end_comment"}
        await update.message.reply_text(message)
        await ask_for_comment(update.message)

    elif text == "Текущая длительность сна":
        message = bot_logic.get_current_duration(user_id)
        await update.message.reply_text(message)

    elif text == "Время с последнего сна":
        message = bot_logic.get_last_sleep_duration(user_id)
        await update.message.reply_text(message)

    elif text == "Добавить пропущенный сон":
        await update.message.reply_text("Введите данные о пропущенном сне в формате:\n\n"
                                        "Начало: dd.mm.yyyy HH:MM\nКонец: dd.mm.yyyy HH:MM")
        user_states[user_id] = {"action": "missed_sleep"}

    elif text == "Статистика за сегодня":
        stats = bot_logic.generate_daily_statistics(user_id)
        await update.message.reply_text(stats)

    elif text == "Да":
        # Пользователь решил добавить комментарий
        if user_id in user_states and "action" in user_states[user_id]:
            user_states[user_id]["waiting_for_comment"] = True
            await update.message.reply_text("Введите ваш комментарий:")

    elif text == "Нет":
        # Пользователь отказался от добавления комментария
        if user_id in user_states:
            user_states.pop(user_id, None)
        await update.message.reply_text("Комментарий не добавлен.")
        await show_main_menu(update)

    elif user_id in user_states and user_states[user_id].get("waiting_for_comment"):
        # Пользователь вводит комментарий
        comment = update.message.text
        action = user_states[user_id]["action"]

        if action == "start_comment":
            bot_logic.add_start_comment(user_id, comment)
        elif action == "end_comment":
            bot_logic.add_end_comment(user_id, comment)

        user_states.pop(user_id, None)
        await update.message.reply_text("Комментарий добавлен.")
        await show_main_menu(update)

    elif user_id in user_states and user_states[user_id]["action"] == "missed_sleep":
        # Обработка добавления пропущенного сна
        try:
            data = update.message.text.split("\n")
            start_time = datetime.strptime(data[0].split(": ")[1], "%d.%m.%Y %H:%M")
            end_time = datetime.strptime(data[1].split(": ")[1], "%d.%m.%Y %H:%M")
            result = bot_logic.add_missed_sleep(user_id, start_time, end_time)
            await update.message.reply_text(result)
        except Exception:
            await update.message.reply_text("Ошибка ввода. Попробуйте снова.")
        user_states.pop(user_id, None)
        await show_main_menu(update)

async def ask_for_comment(message):
    """Задает вопрос о добавлении комментария."""
    keyboard = ReplyKeyboardMarkup(
        [["Да", "Нет"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.reply_text("Добавить комментарий?", reply_markup=keyboard)

async def show_main_menu(update):
    """Показывает главное меню через статичное поле."""
    keyboard = ReplyKeyboardMarkup(
        [["Начать сон", "Закончить сон"],
         ["Текущая длительность сна", "Время с последнего сна"],
         ["Добавить пропущенный сон", "Статистика за сегодня"]],
        resize_keyboard=True,
    )
    if hasattr(update, "message") and update.message:
        await update.message.reply_text("Выберите действие через кнопки ниже.", reply_markup=keyboard)
    elif hasattr(update, "callback_query") and update.callback_query.message:
        await update.callback_query.message.reply_text("Выберите действие через кнопки ниже.", reply_markup=keyboard)

def register_handlers(dispatcher):
    """Регистрирует обработчики."""
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(handle_buttons))
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))