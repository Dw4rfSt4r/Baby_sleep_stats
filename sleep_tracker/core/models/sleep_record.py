"""
Модуль, содержащий класс SleepRecord для хранения информации о периоде сна ребенка.

Этот модуль демонстрирует несколько важных концепций Python:
1. Использование dataclasses для создания классов данных
2. Типизация с помощью аннотаций типов
3. Работа с датами и временем
4. Свойства (properties) и их использование
5. Валидация данных
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple


@dataclass
class SleepRecord:
    """
    Класс для хранения информации о периоде сна ребенка.
    
    Мы используем декоратор @dataclass, который автоматически создает:
    - метод __init__ для инициализации объекта
    - методы __repr__ и __eq__ для строкового представления и сравнения
    - и другие полезные методы
    
    Attributes:
        start_time (datetime): Время начала сна
        end_time (Optional[datetime]): Время окончания сна (None если сон еще не закончен)
        comment (str): Комментарий к записи о сне
    """
    
    start_time: datetime
    end_time: Optional[datetime] = None
    comment: str = ""
    
    def __post_init__(self) -> None:
        """
        Метод для валидации данных после инициализации.
        Вызывается автоматически после __init__ в dataclass.
        
        Raises:
            ValueError: Если время окончания раньше времени начала
        """
        if self.end_time and self.end_time < self.start_time:
            raise ValueError(
                f"Время окончания сна ({self.end_time}) "
                f"не может быть раньше времени начала ({self.start_time})"
            )
    
    @property
    def is_daytime(self) -> bool:
        """
        Определяет, является ли сон дневным на основе времени начала сна.
        
        Property (свойство) - это метод, который можно использовать как атрибут.
        Например: sleep_record.is_daytime вместо sleep_record.is_daytime()
        
        Returns:
            bool: True если это дневной сон (между 8:00 и 20:00), False если ночной
        """
        return 8 <= self.start_time.hour < 20
    
    @property
    def duration(self) -> Tuple[int, int]:
        """
        Рассчитывает продолжительность сна в формате (часы, минуты).
        Если сон еще активен, считает длительность до текущего момента.
        
        Returns:
            Tuple[int, int]: Кортеж (часы, минуты), показывающий длительность сна
        """
        # Определяем конечное время: текущее время для активного сна или время окончания для завершенного
        end = datetime.now() if self.end_time is None else self.end_time
        
        # Вычисляем разницу во времени
        duration = end - self.start_time
        
        # Получаем общее количество минут
        total_minutes = int(duration.total_seconds() / 60)
        
        # Разбиваем на часы и минуты
        hours = total_minutes // 60  # целочисленное деление
        minutes = total_minutes % 60  # остаток от деления
        
        return hours, minutes
    
    def format_duration(self) -> str:
        """
        Форматирует длительность сна в строку вида "чч:мм".
        
        Returns:
            str: Строка с длительностью в формате "чч:мм"
        """
        hours, minutes = self.duration
        return f"{hours:02d}:{minutes:02d}"
    
    def end_sleep(self, end_time: datetime) -> None:
        """
        Завершает период сна.
        
        Args:
            end_time (datetime): Время окончания сна
            
        Raises:
            ValueError: Если время окончания раньше времени начала
        """
        if end_time < self.start_time:
            raise ValueError(
                f"Время окончания сна ({end_time}) "
                f"не может быть раньше времени начала ({self.start_time})"
            )
        self.end_time = end_time
    
    def is_active(self) -> bool:
        """
        Проверяет, является ли запись текущим (активным) сном.
        
        Returns:
            bool: True если сон еще не закончен (end_time is None), False иначе
        """
        return self.end_time is None 