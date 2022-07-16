from datetime import datetime
from enums.match_result import MatchResult
from database.models import EloRateHistory
from services.common.elo_rate_calculator import EloRateCalculator
from app import app


class SingleMatchEloRateManager:
    START_RATE = 1300

    def __init__(self, db):
        self.__db = db

    def __add_rate(self,
                   player_id: int,
                   match_id: int,
                   value: int):
        with app.app_context():
            entity = EloRateHistory(
                player_id=player_id,
                match_id=match_id,
                value=value,
                datetime=datetime.utcnow()
            )
            self.__db.session.add(entity)
            self.__db.session.commit()

    def get(self, player_id: int) -> int:
        with app.app_context():
            rate = EloRateHistory.query.filter(EloRateHistory.player_id == player_id).order_by(
                EloRateHistory.datetime.desc()).first()
            return rate.value if rate else SingleMatchEloRateManager.START_RATE

    def update(self,
               player_1_id: int,
               player_2_id: int,
               match_id: int,
               match_result: MatchResult) -> tuple[int, int]:
        player_1_rate = self.get(player_1_id)
        player_2_rate = self.get(player_2_id)

        player_1_new_rate, player_2_new_rate = EloRateCalculator.calculate(player_1_rate, player_2_rate, match_result)

        with app.app_context():
            self.__add_rate(player_1_id, match_id, player_1_new_rate)
            self.__add_rate(player_2_id, match_id, player_2_new_rate)

        return player_1_new_rate, player_2_new_rate
