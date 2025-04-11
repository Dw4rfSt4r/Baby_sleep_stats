# Пример простой базы данных на основе словаря
db = {
    "users": {}  # Каждому пользователю соответствует список его сеансов сна
}

def save_session(user_id, session):
    """Сохраняет сеанс сна в базу данных."""
    if user_id not in db["users"]:
        db["users"][user_id] = []
    db["users"][user_id].append(session)

def get_sessions_for_user(user_id):
    """Получает все сеансы сна для пользователя."""
    return db["users"].get(user_id, [])

def clear_user_sessions(user_id):
    """Очищает все сеансы сна для пользователя."""
    if user_id in db["users"]:
        db["users"][user_id] = []