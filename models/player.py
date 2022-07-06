from typing import Optional
from datetime import datetime


class Player:
    def __init__(self,
                 id: int,
                 name: str,
                 telegram_id: Optional[int],
                 is_active: bool,
                 creation_date_time: datetime):
        self.id = id
        self.name = name
        self.telegram_id = telegram_id
        self.is_active = is_active
        self.creation_date_time = creation_date_time
