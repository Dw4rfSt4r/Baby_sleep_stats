from datetime import datetime
from bot.sleep import Sleep
from bot.utils import format_datetime
from bot.database import save_session, get_sessions_for_user

user_sessions = {}

def start_sleep(user_id):
    """Начало сна для пользователя."""
    sleep_session = Sleep(start_time=datetime.now())
    user_sessions[user_id] = sleep_session
    return f"Сон начат: {format_datetime(sleep_session.start_time)}"

def end_sleep(user_id):
    """Завершение сна для пользователя."""
    if user_id not in user_sessions or not user_sessions[user_id].start_time:
        return "Вы еще не начали сон. Пожалуйста, начните сон."
    
    sleep_session = user_sessions[user_id]
    sleep_session.set_times(end_time=datetime.now())
    save_session(user_id, sleep_session)
    return f"Сон завершен: {sleep_session.get_report()}"

def add_start_comment(user_id, comment):
    """Добавляет комментарий к началу сна."""
    if user_id in user_sessions:
        user_sessions[user_id].start_comment = comment

def add_end_comment(user_id, comment):
    """Добавляет комментарий к концу сна."""
    if user_id in user_sessions:
        user_sessions[user_id].end_comment = comment

def add_missed_sleep(user_id, start_time, end_time):
    """Добавляет пропущенный сон."""
    missed_sleep = Sleep(start_time=start_time, end_time=end_time)
    save_session(user_id, missed_sleep)
    return "Пропущенный сон добавлен."

def get_current_duration(user_id):
    """Текущая длительность сна."""
    if user_id not in user_sessions or not user_sessions[user_id].start_time:
        return "Сон еще не начат."
    
    sleep_session = user_sessions[user_id]
    if not sleep_session.end_time:
        duration = datetime.now() - sleep_session.start_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes = remainder // 60
        return f"Текущая длительность сна: {int(hours)}ч {int(minutes)}м."
    
    return "Сон уже завершен."

def get_last_sleep_duration(user_id):
    """Время с момента последнего сна."""
    sessions = get_sessions_for_user(user_id)
    if not sessions:
        return "Данных о последнем сне нет."

    last_session = sessions[-1]  # Последний сеанс
    if not last_session.end_time:
        return "Последний сон еще не завершен."

    time_since_last_sleep = datetime.now() - last_session.end_time
    hours, remainder = divmod(time_since_last_sleep.total_seconds(), 3600)
    minutes = remainder // 60
    return f"С момента последнего сна прошло: {int(hours)}ч {int(minutes)}м."

def generate_daily_statistics(user_id):
    """Генерирует статистику за текущий день."""
    sessions = get_sessions_for_user(user_id)
    if not sessions:
        return "Данных за сегодня нет."

    now = datetime.now()
    start_of_day = datetime(now.year, now.month, now.day)

    # Разделяем на категории
    night_sleep = []
    day_naps = []
    for session in sessions:
        if session.start_time < start_of_day and session.end_time >= start_of_day:
            night_sleep.append(session)
        elif session.start_time >= start_of_day:
            day_naps.append(session)

    # Формируем  отчет
    report = "Ночной сон:\n"
    report += "\n".join([f"{format_datetime(s.start_time)} - {format_datetime(s.end_time)}" for s in night_sleep])
    report += "\n\nДневные сны:\n"
    report += "\n".join([f"{format_datetime(s.start_time)} - {format_datetime(s.end_time)}" for s in day_naps])
    return report