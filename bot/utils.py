import pandas as pd  # Импорт pandas
import matplotlib.pyplot as plt  # Импорт matplotlib.pyplot

def generate_excel_and_chart(sessions):
    # Преобразование данных в DataFrame
    df = pd.DataFrame(sessions, columns=["start_time", "start_comment", "end_time", "end_comment", "duration"])
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

    # Заполнение пустых комментариев значением по умолчанию
    df["start_comment"] = df["start_comment"].fillna("Без комментария")
    df["end_comment"] = df["end_comment"].fillna("Без комментария")

    # Форматирование продолжительности в "часы:минуты"
    df["Длительность сна"] = df["duration"].apply(format_duration)

    # Удаление неинформативного столбца duration
    df.drop(columns=["duration"], inplace=True)

    excel_path = "sleep_stats.xlsx"
    chart_path = "sleep_chart.png"

    # Сохранение в Excel с русифицированными заголовками
    df.rename(
        columns={
            "start_time": "Начало сна",
            "start_comment": "Комментарий к началу сна",
            "end_time": "Конец сна",
            "end_comment": "Комментарий к окончанию сна",
        },
        inplace=True,
    )
    df.to_excel(excel_path, index=False)

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.bar(df["Начало сна"].dt.date, df["Длительность сна"].apply(lambda x: float(x.split(":")[0]) + float(x.split(":")[1]) / 60), color="skyblue")
    plt.xlabel("Дата")
    plt.ylabel("Длительность сна (часы)")
    plt.title("Статистика сна")
    plt.xticks(rotation=45)

    # Добавление текста с часами и минутами над каждым столбцом
    for i, row in df.iterrows():
        duration_hm = row["Длительность сна"]
        plt.text(
            x=row["Начало сна"].date(),
            y=float(duration_hm.split(":")[0]) + float(duration_hm.split(":")[1]) / 60 + 0.1,  # Смещение текста над столбцом
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