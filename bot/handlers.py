from datetime import datetime
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
from . import bot_logic

# Состояние для отслеживания действий пользователей
user_states = {}

async def start(update, context):
    """Обработчик команды /start. Показывает главное меню."""
    await show_main_menu(update)

async def handle_buttons(update, context):
    """Обработчик нажатий на кнопки."""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    try:
        if query.data == "start_sleep":
            # Начать сон
            message = bot_logic.start_sleep(user_id)
            user_states[user_id] = {"action": "start_comment", "waiting_for_comment": False}
            await query.message.reply_text(message)
            await ask_for_comment(query.message)

        elif query.data == "end_sleep":
            # Завершить сон
            user_states[user_id] = {"action": "end_comment", "waiting_for_comment": False}
            await ask_for_comment(query.message)

        elif query.data == "current_sleep_duration":
            # Текущая длительность сна
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
            # Статистика за сегодня
            stats = bot_logic.generate_daily_statistics(user_id)
            if stats:
                await query.message.reply_text(stats)
            else:
                await query.message.reply_text("Статистика за сегодня отсутствует.")

    except Exception as e:
        await query.message.reply_text(f"Ошибка при обработке кнопки: {str(e)}")

async def handle_text(update, context):
    """Обработчик текстовых сообщений."""
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        if text == "Главное меню":
            await show_main_menu(update)
            return

        if user_id in user_states:
            state = user_states[user_id]
            action = state.get("action")
            waiting_for_comment = state.get("waiting_for_comment", False)

            if waiting_for_comment:
                # Пользователь вводит комментарий
                comment = text

                if action == "start_comment":
                    bot_logic.add_start_comment(user_id, comment)
                    await update.message.reply_text("Ваш комментарий сохранен.")
                    await show_main_menu(update)

                elif action == "end_comment":
                    bot_logic.add_end_comment(user_id, comment)
                    final_report = bot_logic.end_sleep(user_id)
                    await update.message.reply_text("Ваш комментарий сохранен.")
                    await update.message.reply_text(final_report)
                    await show_main_menu(update)

                user_states.pop(user_id, None)
                return

            if text == "Да":
                # Устанавливаем ожидание ввода комментария
                user_states[user_id]["waiting_for_comment"] = True
                await update.message.reply_text("Введите ваш комментарий:")
                return

            elif text == "Нет":
                # Пропускаем добавление комментария
                if action == "start_comment":
                    await update.message.reply_text("Сон начат.")
                    await show_main_menu(update)

                elif action == "end_comment":
                    final_report = bot_logic.end_sleep(user_id)
                    await update.message.reply_text(final_report)
                    await show_main_menu(update)

                user_states.pop(user_id, None)
                return

        if text == "Начать сон":
            message = bot_logic.start_sleep(user_id)
            user_states[user_id] = {"action": "start_comment", "waiting_for_comment": False}
            await update.message.reply_text(message)
            await ask_for_comment(update.message)

        elif text == "Закончить сон":
            user_states[user_id] = {"action": "end_comment", "waiting_for_comment": False}
            await ask_for_comment(update.message)

        elif text == "Текущая длительность сна":
            # Обработка кнопки "Текущая длительность сна"
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
            # Обработка кнопки "Статистика за сегодня"
            stats = bot_logic.generate_daily_statistics(user_id)
            if stats:
                await update.message.reply_text(stats)
            else:
                await update.message.reply_text("Статистика за сегодня отсутствует.")

        # Обработка добавления пропущенного сна
        elif user_id in user_states and user_states[user_id]["action"] == "missed_sleep":
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

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

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