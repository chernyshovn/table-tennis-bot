from typing import Optional
import enum


class MatchResult(enum.Enum):
    FIRST_PLAYER_WON = 0
    SECOND_PLAYER_WON = 1
    DRAW = 2


class MatchStatistic:
    def __init__(self,
                 result: MatchResult,
                 player_1_telegram_id: Optional[int],
                 player_2_telegram_id: Optional[int],
                 description: str):
        self.result = result
        self.player_1_telegram_id = player_1_telegram_id
        self.player_2_telegram_id = player_2_telegram_id
        self.description = description
        