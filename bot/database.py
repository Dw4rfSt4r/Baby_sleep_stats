import sqlite3
import os

DB_PATH = "sleep_tracker.db"

def init_db():
    """Инициализация базы данных. Создаёт файл, если его нет, и таблицу sleep_sessions."""
    # Проверка, является ли существующий файл корректной базой данных
    if os.path.exists(DB_PATH) and not is_valid_database(DB_PATH):
        raise sqlite3.DatabaseError(f"Файл {DB_PATH} не является базой данных SQLite. Удалите его и попробуйте снова.")

    # Подключение к базе данных и создание таблицы, если её нет
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sleep_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        start_time TEXT,
        end_time TEXT,
        duration REAL,
        start_comment TEXT,
        end_comment TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_session(user_id, session):
    """Сохраняет сеанс сна пользователя в базу данных."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO sleep_sessions (user_id, start_time, end_time, duration, start_comment, end_comment)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        session.get("start_time").isoformat(),
        session.get("end_time").isoformat(),
        session.get("duration"),
        session.get("start_comment"),
        session.get("end_comment"),
    ))
    conn.commit()
    conn.close()

def get_sessions_for_user(user_id):
    """Возвращает все сеансы сна для указанного пользователя."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT start_time, end_time, duration FROM sleep_sessions WHERE user_id = ?
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def is_valid_database(db_path):
    """Проверяет, является ли файл корректной базой данных SQLite."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        conn.close()
        return True
    except sqlite3.DatabaseError:
        return False