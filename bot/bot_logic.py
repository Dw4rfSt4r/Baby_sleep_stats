import os
import pandas as pd
from datetime import datetime
from bot.sleep import Sleep
from bot.utils import format_datetime
from bot.database import save_session, get_sessions_for_user

# Состояние пользователей (связь ID пользователя с объектом Sleep)
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
    
    # Сохранение в базу данных
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

def export_statistics_to_excel(user_id):
    """Экспортирует статистику сна в Excel-файл."""
    sessions = get_sessions_for_user(user_id)
    if not sessions:
        return None

    data = [{
        "Дата начала": session.start_time.strftime("%d.%m.%Y %H:%M"),
        "Дата окончания": session.end_time.strftime("%d.%m.%Y %H:%M") if session.end_time else "Не завершено",
        "Длительность (часы)": round(session.duration.total_seconds() / 3600, 2) if session.duration else None,
        "Комментарий к началу": session.start_comment,
        "Комментарий к концу": session.end_comment,
    } for session in sessions]
    
    df = pd.DataFrame(data)
    file_path = f"user_{user_id}_sleep_statistics.xlsx"
    df.to_excel(file_path, index=False)
    return file_path