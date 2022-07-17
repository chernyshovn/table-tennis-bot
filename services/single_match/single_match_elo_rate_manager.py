from datetime import datetime
from database.models import EloRateHistory, SingleMatchStatistic
from models.single_match_elo_rate import SingleMatchEloRate
from services.common.elo_rate_calculator import EloRateCalculator
from services.common.player_manager import PlayerManager
from app import app


class SingleMatchEloRateManager:
    START_RATE = 1300

    def __init__(self, db, player_manager: PlayerManager):
        self.__db = db
        self.__player_manager = player_manager

    def __add_rate(self,
                   player_id: int,
                   match_id: int,
                   value: int,
                   date_time: datetime):
        with app.app_context():
            entity = EloRateHistory(
                player_id=player_id,
                match_id=match_id,
                value=value,
                datetime=date_time
            )
            self.__db.session.add(entity)
            self.__db.session.commit()

    def get(self, player_id: int) -> int:
        with app.app_context():
            rate = EloRateHistory.query.filter(EloRateHistory.player_id == player_id).order_by(
                EloRateHistory.datetime.desc()).first()
            return rate.value if rate else SingleMatchEloRateManager.START_RATE

    def update(self,
               match_id: int,
               player_1_id: int,
               player_2_id: int,
               player_1_game_won_count: int,
               player_2_game_won_count: int,
               date_time: datetime
             ) -> tuple[int, int]:
        player_1_rate = self.get(player_1_id)
        player_2_rate = self.get(player_2_id)

        player_1_new_rate, player_2_new_rate = EloRateCalculator.calculate(
            player_1_rate,
            player_2_rate,
            player_1_game_won_count,
            player_2_game_won_count
        )

        with app.app_context():
            self.__add_rate(player_1_id, match_id, player_1_new_rate, date_time)
            self.__add_rate(player_2_id, match_id, player_2_new_rate, date_time)

        return player_1_new_rate, player_2_new_rate

    def recalculate_all(self):
        with app.app_context():
            self.__db.session.query(EloRateHistory).delete()
            self.__db.session.commit()
            self.__db.engine.execute("ALTER TABLE elo_rate_history AUTO_INCREMENT = 1;")

            statistics = SingleMatchStatistic.query.order_by(SingleMatchStatistic.end_date_time).all()
            for statistic in statistics:
                self.update(
                    match_id=statistic.match_id,
                    player_1_id=statistic.player_1_id,
                    player_2_id=statistic.player_2_id,
                    player_1_game_won_count=statistic.player_1_game_won_count,
                    player_2_game_won_count=statistic.player_2_game_won_count,
                    date_time=statistic.end_date_time
                )

    def list(self) -> list[SingleMatchEloRate]:
        with app.app_context():
            rates = [
                SingleMatchEloRate(
                    player_name=player.name,
                    value=self.get(player.id)
                )
                for player in self.__player_manager.list_all()
            ]
            return sorted(rates, key=lambda rate: rate.value, reverse=True)
