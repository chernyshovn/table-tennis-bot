from typing import Optional
from datetime import datetime
from enums.match_result import MatchResult


class SingleMatchTelegramStatistic:
    def __init__(self,
                 result: MatchResult,
                 player_1_id: int,
                 player_2_id: int,
                 player_1_telegram_id: Optional[int],
                 player_2_telegram_id: Optional[int],
                 player_1_games_won: int,
                 player_2_games_won: int,
                 player_1_points_won: int,
                 player_2_points_won: int,
                 start_date_time: datetime,
                 end_date_time: datetime,
                 description: str):
        self.result = result
        self.player_1_id = player_1_id
        self.player_2_id = player_2_id
        self.player_1_telegram_id = player_1_telegram_id
        self.player_2_telegram_id = player_2_telegram_id
        self.player_1_games_won = player_1_games_won
        self.player_2_games_won = player_2_games_won
        self.player_1_points_won = player_1_points_won
        self.player_2_points_won = player_2_points_won
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.description = description

    def is_no_games(self) -> bool:
        return (self.player_1_points_won == 0) and (self.player_2_points_won == 0)
