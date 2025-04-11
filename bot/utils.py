import matplotlib.pyplot as plt
import pandas as pd

def generate_excel_and_chart(sessions, user_id):
    """Генерирует Excel файл и график на основе сеансов сна."""
    # Создаем DataFrame для сеансов сна
    data = [{
        "start_time": session.start_time,
        "end_time": session.end_time,
        "duration": session.duration.total_seconds() / 3600,
        "start_comment": session.start_comment,
        "end_comment": session.end_comment
    } for session in sessions]
    
    df = pd.DataFrame(data)
    
    # Генерация Excel файла
    excel_path = f"user_{user_id}_sleep_data.xlsx"
    df.to_excel(excel_path, index=False)
    
    # Генерация графика
    plt.figure(figsize=(10, 6))
    plt.bar(df["start_time"], df["duration"], color="skyblue")
    plt.xlabel("Дата")
    plt.ylabel("Длительность сна (часы)")
    plt.title("История сна")
    chart_path = f"user_{user_id}_sleep_chart.png"
    plt.savefig(chart_path)
    plt.close()
    
    return excel_path, chart_path

def format_datetime(dt):
    """Форматирует дату и время в формате dd.mm.yyyy HH:MM."""
    return dt.strftime("%d.%m.%Y %H:%M")