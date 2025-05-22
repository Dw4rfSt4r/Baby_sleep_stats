"""
Модуль, содержащий класс Child для хранения информации о ребенке.

Этот модуль демонстрирует:
1. Работу с коллекциями (списки записей сна)
2. Валидацию данных
3. Вычисляемые свойства
4. Управление связанными объектами
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple

from .sleep_record import SleepRecord


@dataclass
class Child:
    """
    Класс для хранения информации о ребенке и управления его записями сна.
    
    Attributes:
        name (str): Имя ребенка
        birth_date (date): Дата рождения
        sleep_records (List[SleepRecord]): Список записей о сне
    """
    
    name: str
    birth_date: date
    sleep_records: List[SleepRecord] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """
        Валидация данных после инициализации.
        
        Raises:
            ValueError: Если дата рождения в будущем
        """
        if self.birth_date > date.today():
            raise ValueError("Дата рождения не может быть в будущем")
    
    @property
    def age_months(self) -> int:
        """
        Вычисляет возраст ребенка в месяцах.
        
        Returns:
            int: Возраст в месяцах
        """
        today = date.today()
        return (
            (today.year - self.birth_date.year) * 12
            + (today.month - self.birth_date.month)
            - (today.day < self.birth_date.day)
        )
    
    def get_active_sleep(self) -> Optional[SleepRecord]:
        """
        Возвращает текущую активную запись о сне, если она есть.
        
        Returns:
            Optional[SleepRecord]: Активная запись о сне или None
        """
        for record in reversed(self.sleep_records):
            if record.is_active():
                return record
        return None
    
    def start_sleep(self, start_time: datetime, comment: str = "") -> SleepRecord:
        """
        Создает новую запись о сне.
        
        Args:
            start_time (datetime): Время начала сна
            comment (str, optional): Комментарий к записи
            
        Returns:
            SleepRecord: Новая запись о сне
            
        Raises:
            ValueError: Если уже есть активная запись о сне
        """
        if self.get_active_sleep():
            raise ValueError("Уже есть активная запись о сне. Чтобы начать новый сон, необходимо завершить текущий")
        
        record = SleepRecord(start_time=start_time, comment=comment)
        self.sleep_records.append(record)
        return record
    
    def end_sleep(self, end_time: datetime, comment: Optional[str] = None) -> SleepRecord:
        """
        Завершает активную запись о сне.
        
        Args:
            end_time (datetime): Время окончания сна
            comment (Optional[str]): Дополнительный комментарий к записи
            
        Returns:
            SleepRecord: Завершенная запись о сне
            
        Raises:
            ValueError: Если нет активной записи о сне
        """
        active_sleep = self.get_active_sleep()
        if not active_sleep:
            raise ValueError("Нет активной записи о сне")
        
        active_sleep.end_sleep(end_time)
        if comment:
            active_sleep.comment += f"\n{comment}"
        
        return active_sleep
    
    def get_sleep_stats(self, date_: Optional[date] = None) -> Tuple[int, int, List[SleepRecord]]:
        """
        Возвращает статистику сна за указанный день.
        По умолчанию возвращает статистику за сегодня.
        
        В статистику включаются:
        1. Ночной сон, который закончился в указанную дату (даже если начался днем ранее)
        2. Все дневные сны за указанную дату
        
        Args:
            date_ (Optional[date]): Дата, за которую нужна статистика. 
                                  Если не указана, используется текущая дата.
            
        Returns:
            Tuple[int, int, List[SleepRecord]]: (общее время сна в минутах,
                                                общее время бодрствования в минутах,
                                                список записей о сне за день)
        """
        target_date = date_ or date.today()
        
        # Собираем записи о сне:
        # 1. Ночной сон, который закончился в этот день
        # 2. Дневные сны этого дня
        day_records = []
        
        for record in self.sleep_records:
            if not record.end_time:  # Пропускаем незавершенные записи
                continue
                
            # Ночной сон, который закончился в этот день
            if record.end_time.date() == target_date and record.start_time.date() < target_date:
                day_records.append(record)
            # Дневные сны этого дня (исключаем сны, которые закончились на следующий день)
            elif (record.start_time.date() == target_date and 
                  record.end_time.date() == target_date):
                day_records.append(record)
        
        # Считаем общее время сна
        total_sleep_minutes = 0
        for record in day_records:
            if record.duration:  # Если сон завершен
                start = record.start_time
                end = record.end_time
                
                # Для ночного сна берем только часть от начала дня до окончания
                if start.date() < target_date:
                    start = datetime.combine(target_date, datetime.min.time())
                
                duration = end - start
                total_sleep_minutes += int(duration.total_seconds() / 60)
        
        # Считаем время бодрствования (24 часа минус время сна)
        total_awake_minutes = 24 * 60 - total_sleep_minutes
        
        return total_sleep_minutes, total_awake_minutes, day_records 