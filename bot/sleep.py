from datetime import datetime, timedelta

class Sleep:
    def __init__(self, start_time=None, end_time=None, start_comment=None, end_comment=None):
        self.start_time = start_time
        self.end_time = end_time
        self.start_comment = start_comment
        self.end_comment = end_comment

    @property
    def duration(self):
        """Рассчитывает длительность сна на основе начала и конца."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta
        return None

    def set_times(self, start_time=None, end_time=None):
        """Позволяет вручную изменить время начала или конца сна."""
        if start_time:
            self.start_time = start_time
        if end_time:
            self.end_time = end_time

    def get_report(self):
        """Возвращает отчет о сеансе сна."""
        duration = self.duration
        duration_str = f"{duration.seconds // 3600}ч {duration.seconds % 3600 // 60}м" if duration else "Неизвестно"
        return (f"Начало сна: {self.start_time.strftime('%d.%m.%Y %H:%M:%S')}\n"
                f"Конец сна: {self.end_time.strftime('%d.%m.%Y %H:%M:%S') if self.end_time else 'Еще не завершено'}\n"
                f"Длительность: {duration_str}\n"
                f"Комментарий к началу: {self.start_comment}\n"
                f"Комментарий к концу: {self.end_comment}")