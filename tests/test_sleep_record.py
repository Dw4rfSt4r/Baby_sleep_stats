"""
Модуль с тестами для класса SleepRecord.

Демонстрирует:
1. Написание тестов с помощью pytest
2. Работу с исключениями в тестах
3. Проверку граничных случаев
4. Тестирование с использованием фиксированного времени
"""

from datetime import datetime, timedelta
import pytest
from unittest.mock import patch

from sleep_tracker.core.models.sleep_record import SleepRecord


def test_create_sleep_record():
    """Тест создания записи о сне"""
    # Подготовка данных
    start_time = datetime(2024, 3, 15, 20, 30)  # 20:30
    
    # Выполнение действия
    record = SleepRecord(start_time=start_time)
    
    # Проверка результатов
    assert record.start_time == start_time
    assert record.end_time is None
    assert record.comment == ""


def test_is_daytime():
    """Тест определения дневного/ночного сна"""
    # Дневной сон (в 14:00)
    day_sleep = SleepRecord(start_time=datetime(2024, 3, 15, 14, 0))
    assert day_sleep.is_daytime is True
    
    # Ночной сон (в 20:00)
    night_sleep = SleepRecord(start_time=datetime(2024, 3, 15, 20, 0))
    assert night_sleep.is_daytime is False


def test_completed_sleep_duration():
    """Тест расчета продолжительности завершенного сна"""
    # Создаем запись о сне длительностью 2 часа 30 минут
    start_time = datetime(2024, 3, 15, 20, 0)
    end_time = datetime(2024, 3, 15, 22, 30)
    record = SleepRecord(start_time=start_time, end_time=end_time)
    
    # Проверяем продолжительность
    hours, minutes = record.duration
    assert hours == 2
    assert minutes == 30
    
    # Проверяем форматированный вывод
    assert record.format_duration() == "02:30"


@patch('sleep_tracker.core.models.sleep_record.datetime')
def test_active_sleep_duration(mock_datetime):
    """Тест расчета продолжительности активного сна"""
    # Фиксируем текущее время
    start_time = datetime(2024, 3, 15, 20, 0)
    current_time = datetime(2024, 3, 15, 21, 45)  # 1 час 45 минут спустя
    mock_datetime.now.return_value = current_time
    
    # Создаем запись об активном сне
    record = SleepRecord(start_time=start_time)
    
    # Проверяем продолжительность
    hours, minutes = record.duration
    assert hours == 1
    assert minutes == 45
    
    # Проверяем форматированный вывод
    assert record.format_duration() == "01:45"


def test_invalid_end_time():
    """Тест на проверку исключения при неверном времени окончания"""
    start_time = datetime(2024, 3, 15, 20, 0)
    end_time = datetime(2024, 3, 15, 19, 0)  # Время окончания РАНЬШЕ начала
    
    # Проверяем, что создание записи с неверным временем вызовет исключение
    with pytest.raises(ValueError):
        SleepRecord(start_time=start_time, end_time=end_time)


def test_end_sleep():
    """Тест метода завершения сна"""
    # Создаем запись о сне
    start_time = datetime(2024, 3, 15, 20, 0)
    record = SleepRecord(start_time=start_time)
    
    # Проверяем, что сон активен
    assert record.is_active() is True
    
    # Завершаем сон
    end_time = datetime(2024, 3, 15, 22, 30)
    record.end_sleep(end_time)
    
    # Проверяем, что сон завершен
    assert record.is_active() is False
    assert record.end_time == end_time 