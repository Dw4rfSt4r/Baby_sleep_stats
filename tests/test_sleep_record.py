"""
Модуль с тестами для класса SleepRecord.

Демонстрирует:
1. Написание тестов с помощью pytest
2. Работу с исключениями в тестах
3. Проверку граничных случаев
4. Использование фикстур и моков
"""

from datetime import datetime, timedelta
import pytest
from unittest.mock import patch

from sleep_tracker.core.models.sleep_record import SleepRecord


@pytest.fixture
def sample_sleep_record():
    """
    Фикстура - специальная функция в pytest, которая подготавливает данные для тестов.
    Каждый тест, который использует эту фикстуру, получит свежий экземпляр SleepRecord.
    """
    return SleepRecord(
        start_time=datetime(2024, 3, 15, 20, 30),  # 20:30
        comment="Уснул быстро"
    )


def test_create_sleep_record(sample_sleep_record):
    """
    Тест создания записи о сне.
    Проверяем, что:
    1. Объект создается с правильными начальными значениями
    2. Необязательные поля имеют правильные значения по умолчанию
    """
    assert sample_sleep_record.start_time == datetime(2024, 3, 15, 20, 30)
    assert sample_sleep_record.end_time is None
    assert sample_sleep_record.comment == "Уснул быстро"


def test_is_daytime():
    """
    Тест определения дневного/ночного сна.
    Проверяем граничные случаи:
    1. Середина дня (дневной сон)
    2. Поздний вечер (ночной сон)
    3. Раннее утро (ночной сон)
    4. Граничное время
    """
    # Дневной сон (14:00)
    day_sleep = SleepRecord(start_time=datetime(2024, 3, 15, 14, 0))
    assert day_sleep.is_daytime is True
    
    # Ночной сон (22:00)
    night_sleep = SleepRecord(start_time=datetime(2024, 3, 15, 22, 0))
    assert night_sleep.is_daytime is False
    
    # Ранее утро (5:00)
    early_sleep = SleepRecord(start_time=datetime(2024, 3, 15, 5, 0))
    assert early_sleep.is_daytime is False
    
    # Граничное время (8:00 - начало дневного времени)
    border_day = SleepRecord(start_time=datetime(2024, 3, 15, 8, 0))
    assert border_day.is_daytime is True
    
    # Граничное время (19:59 - всё еще день)
    border_night = SleepRecord(start_time=datetime(2024, 3, 15, 19, 59))
    assert border_night.is_daytime is True


def test_completed_sleep_duration(sample_sleep_record):
    """
    Тест расчета продолжительности завершенного сна.
    Проверяем:
    1. Точность расчета часов и минут
    2. Форматирование вывода
    """
    # Завершаем сон через 2 часа 30 минут
    end_time = sample_sleep_record.start_time + timedelta(hours=2, minutes=30)
    sample_sleep_record.end_sleep(end_time)
    
    # Проверяем расчет продолжительности
    hours, minutes = sample_sleep_record.duration
    assert hours == 2
    assert minutes == 30
    
    # Проверяем форматированный вывод
    assert sample_sleep_record.format_duration() == "02:30"


@patch('sleep_tracker.core.models.sleep_record.datetime')
def test_active_sleep_duration(mock_datetime, sample_sleep_record):
    """
    Тест расчета продолжительности активного (текущего) сна.
    Используем mock для datetime.now(), чтобы "заморозить" текущее время.
    """
    # Устанавливаем "текущее" время на 1 час 45 минут после начала сна
    current_time = sample_sleep_record.start_time + timedelta(hours=1, minutes=45)
    mock_datetime.now.return_value = current_time
    
    # Проверяем расчет продолжительности текущего сна
    hours, minutes = sample_sleep_record.duration
    assert hours == 1
    assert minutes == 45
    
    # Проверяем форматированный вывод
    assert sample_sleep_record.format_duration() == "01:45"


def test_invalid_end_time(sample_sleep_record):
    """
    Тест на проверку валидации времени окончания сна.
    Проверяем:
    1. Исключение при создании записи с неверным временем
    2. Исключение при попытке завершить сон неверным временем
    """
    # Время окончания раньше времени начала
    invalid_end_time = sample_sleep_record.start_time - timedelta(minutes=30)
    
    # Проверяем, что попытка создать запись вызовет исключение
    with pytest.raises(ValueError) as exc_info:
        SleepRecord(
            start_time=sample_sleep_record.start_time,
            end_time=invalid_end_time
        )
    assert "не может быть раньше времени начала" in str(exc_info.value)
    
    # Проверяем, что попытка завершить сон неверным временем вызовет исключение
    with pytest.raises(ValueError) as exc_info:
        sample_sleep_record.end_sleep(invalid_end_time)
    assert "не может быть раньше времени начала" in str(exc_info.value)


def test_is_active(sample_sleep_record):
    """
    Тест проверки активности записи о сне.
    Проверяем:
    1. Начальное состояние (активный)
    2. Состояние после завершения (неактивный)
    """
    # Проверяем, что новая запись активна
    assert sample_sleep_record.is_active() is True
    
    # Завершаем сон
    end_time = sample_sleep_record.start_time + timedelta(hours=2)
    sample_sleep_record.end_sleep(end_time)
    
    # Проверяем, что запись стала неактивной
    assert sample_sleep_record.is_active() is False 