from typing import Optional
from datetime import datetime, timedelta


class DatetimeUtils:
    @staticmethod
    def to_ddmmyyyy_hhmm(value: datetime, shift: Optional[timedelta] = None) -> str:
        if shift:
            value += shift
        return value.strftime('%d.%m.%Y %H:%M')

    @staticmethod
    def to_hhmm_diff(value1: datetime, value2: datetime) -> str:
        delta = abs(value1 - value2)
        seconds = int(delta.total_seconds())
        hours = seconds // 3600
        minutes = (seconds // 60) - (hours * 60)
        return f'{hours}ч {minutes}м'
