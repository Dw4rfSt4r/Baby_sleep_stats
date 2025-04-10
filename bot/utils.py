import pandas as pd
import matplotlib.pyplot as plt

def generate_excel_and_chart(sessions):
    # Преобразование данных в DataFrame
    df = pd.DataFrame(sessions, columns=["start_time", "end_time", "duration"])
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

    # Форматирование продолжительности в "часы:минуты"
    df["formatted_duration"] = df["duration"].apply(format_duration)

    excel_path = "sleep_stats.xlsx"
    chart_path = "sleep_chart.png"

    # Сохранение в Excel
    df.to_excel(excel_path, index=False, columns=["start_time", "end_time", "formatted_duration"])

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.bar(df["start_time"].dt.date, df["duration"], color="skyblue")
    plt.xlabel("Дата")
    plt.ylabel("Длительность сна (часы)")
    plt.title("Статистика сна")
    plt.xticks(rotation=45)

    # Добавление текста с часами и минутами над каждым столбцом
    for i, row in df.iterrows():
        duration_hm = format_duration(row["duration"])
        plt.text(
            x=row["start_time"].date(),
            y=row["duration"] + 0.1,  # Смещение текста над столбцом
            s=duration_hm,
            ha="center",
            fontsize=10,
            color="black"
        )

    plt.savefig(chart_path)
    plt.close()

    return excel_path, chart_path

def format_duration(duration):
    """Форматирует продолжительность сна из дробного формата в часы:минуты."""
    hours = int(duration)
    minutes = int((duration - hours) * 60)
    return f"{hours}:{minutes:02d}"