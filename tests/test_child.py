"""
Модуль с тестами для класса Child.

Демонстрирует:
1. Использование фикстур
2. Тестирование исключений
3. Тестирование вычисляемых свойств
4. Моки для работы с датами
"""

from datetime import datetime, date, timedelta
import pytest
from unittest.mock import patch

from sleep_tracker.core.models.child import Child


@pytest.fixture
def sample_child():
    """
    Фикстура, создающая тестового ребенка.
    """
    return Child(
        name="Тест",
        birth_date=date(2023, 1, 1)  # Ребенок родился 1 января 2023
    )


def test_create_child(sample_child):
    """
    Тест создания объекта Child.
    Проверяем:
    1. Корректность установки атрибутов
    2. Инициализацию пустого списка записей
    """
    assert sample_child.name == "Тест"
    assert sample_child.birth_date == date(2023, 1, 1)
    assert sample_child.sleep_records == []


def test_invalid_birth_date():
    """
    Тест валидации даты рождения.
    Проверяем, что нельзя создать ребенка с датой рождения в будущем.
    """
    future_date = date.today().replace(year=date.today().year + 1)
    
    with pytest.raises(ValueError) as exc_info:
        Child(name="Тест", birth_date=future_date)
    assert "не может быть в будущем" in str(exc_info.value)


@patch('sleep_tracker.core.models.child.date')
def test_age_months(mock_date, sample_child):
    """
    Тест расчета возраста в месяцах.
    Проверяем различные сценарии:
    1. Полные месяцы
    2. Неполный месяц
    3. Переход через год
    """
    # Устанавливаем текущую дату на 15 марта 2024
    mock_date.today.return_value = date(2024, 3, 15)
    
    # Ребенок родился 1 января 2023, значит возраст 14 месяцев
    assert sample_child.age_months == 14
    
    # Меняем дату рождения на более позднюю
    sample_child.birth_date = date(2023, 3, 20)
    # 15 марта 2024 - 20 марта 2023 = 11 месяцев (неполный 12-й месяц)
    assert sample_child.age_months == 11


def test_start_sleep(sample_child):
    """
    Тест создания новой записи о сне.
    Проверяем:
    1. Создание записи
    2. Добавление в список
    3. Запрет создания при наличии активной записи
    """
    # Создаем первую запись
    start_time = datetime(2024, 3, 15, 20, 30)
    record = sample_child.start_sleep(start_time, "Тестовый сон")
    
    # Проверяем создание записи
    assert record.start_time == start_time
    assert record.comment == "Тестовый сон"
    assert record in sample_child.sleep_records
    
    # Проверяем, что нельзя создать вторую активную запись
    with pytest.raises(ValueError) as exc_info:
        sample_child.start_sleep(datetime(2024, 3, 15, 21, 0))
    assert "Уже есть активная запись о сне" in str(exc_info.value)


def test_end_sleep(sample_child):
    """
    Тест завершения записи о сне.
    Проверяем:
    1. Завершение активной записи
    2. Добавление комментария
    3. Ошибку при отсутствии активной записи
    """
    # Создаем и завершаем запись
    start_time = datetime(2024, 3, 15, 20, 30)
    record = sample_child.start_sleep(start_time)
    
    end_time = datetime(2024, 3, 15, 22, 0)
    ended_record = sample_child.end_sleep(end_time, "Проснулся сам")
    
    # Проверяем завершение
    assert ended_record.end_time == end_time
    assert "Проснулся сам" in ended_record.comment
    assert not ended_record.is_active()
    
    # Проверяем, что нельзя завершить несуществующий сон
    with pytest.raises(ValueError) as exc_info:
        sample_child.end_sleep(datetime(2024, 3, 15, 23, 0))
    assert "Нет активной записи о сне" in str(exc_info.value)


@patch('sleep_tracker.core.models.child.date')
def test_get_sleep_stats(mock_date, sample_child):
    """
    Тест получения статистики сна за день.
    Проверяем:
    1. Подсчет ночного сна, который закончился в указанный день
    2. Подсчет дневных снов
    3. Подсчет времени бодрствования
    4. Фильтрацию записей
    5. Работу с текущей датой по умолчанию
    """
    # Фиксируем текущую дату
    today = date(2024, 3, 15)
    mock_date.today.return_value = today
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    # Создаем записи о сне
    
    # 1. Ночной сон, начавшийся вчера (20:00 - 06:00)
    night_sleep_start = datetime.combine(yesterday, datetime.min.time().replace(hour=20))
    night_sleep_end = datetime.combine(today, datetime.min.time().replace(hour=6))
    sample_child.start_sleep(night_sleep_start, "Ночной сон")
    sample_child.end_sleep(night_sleep_end)
    
    # 2. Дневной сон (13:00 - 15:00)
    day_sleep_start = datetime.combine(today, datetime.min.time().replace(hour=13))
    day_sleep_end = datetime.combine(today, datetime.min.time().replace(hour=15))
    sample_child.start_sleep(day_sleep_start, "Дневной сон")
    sample_child.end_sleep(day_sleep_end)
    
    # 3. Следующий ночной сон (20:00 - 06:00 следующего дня)
    next_night_sleep_start = datetime.combine(today, datetime.min.time().replace(hour=20))
    next_night_sleep_end = datetime.combine(tomorrow, datetime.min.time().replace(hour=6))
    sample_child.start_sleep(next_night_sleep_start, "Следующий ночной сон")
    sample_child.end_sleep(next_night_sleep_end)
    
    # Проверяем статистику за конкретную дату
    sleep_minutes, awake_minutes, records = sample_child.get_sleep_stats(today)
    
    # Отладочная информация
    print(f"\nСтатистика за {today}:")
    print(f"1. Ночной сон: {night_sleep_start} - {night_sleep_end}")
    print(f"2. Дневной сон: {day_sleep_start} - {day_sleep_end}")
    print(f"3. Следующий ночной сон: {next_night_sleep_start} - {next_night_sleep_end}")
    print(f"Всего минут сна: {sleep_minutes}")
    print(f"Минут бодрствования: {awake_minutes}")
    print(f"Количество записей: {len(records)}")
    for record in records:
        print(f"Запись: {record.start_time} - {record.end_time}")
        if record.duration:
            hours, minutes = record.duration
            print(f"Продолжительность: {hours} часов, {minutes} минут")
    
    # За день должно быть учтено:
    # - 6 часов утреннего сна (с 00:00 до 06:00)
    # - 2 часа дневного сна (13:00 - 15:00)
    expected_sleep_minutes = (6 + 2) * 60
    assert sleep_minutes == expected_sleep_minutes
    assert awake_minutes == 24 * 60 - expected_sleep_minutes
    assert len(records) == 2  # Ночной сон и дневной сон
    
    # Проверяем статистику за следующий день
    tomorrow_sleep_minutes, _, tomorrow_records = sample_child.get_sleep_stats(tomorrow)
    assert tomorrow_sleep_minutes == 6 * 60  # Только 6 часов утреннего сна
    assert len(tomorrow_records) == 1  # Только один ночной сон
    
    # Проверяем статистику за текущую дату (без указания даты)
    default_sleep_minutes, default_awake_minutes, default_records = sample_child.get_sleep_stats()
    assert default_sleep_minutes == sleep_minutes
    assert default_awake_minutes == awake_minutes
    assert default_records == records 