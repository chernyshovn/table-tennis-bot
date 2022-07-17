from datetime import datetime


class SingleMatchEloRate:
    def __init__(self,
                 value: int,
                 delta: int,
                 datetime: datetime):
        self.value = value
        self.delta = delta
        self.datetime = datetime
