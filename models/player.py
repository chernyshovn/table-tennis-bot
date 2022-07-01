from typing import Optional


class Player:
    def __init__(self, id: int, name: str, telegram_id: Optional[int]):
        self.id = id
        self.name = name
        self.telegram_id = telegram_id
