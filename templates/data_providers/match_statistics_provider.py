from app import app
from datetime import datetime, timedelta
from database.models import SingleMatchStatistic
from utils.datetime_utils import DatetimeUtils


class MatchStatisticPlayerInfo:
    def __init__(self,
                 id: int,
                 name: str,
                 game_won_count: int,
                 point_won_count: int):
        self.id = id
        self.name = name
        self.game_won_count = game_won_count
        self.point_won_count = point_won_count


class MatchStatistic:
    def __init__(self,
                 match_id: int,
                 location_name: str,
                 start_date_time: datetime,
                 duration: timedelta,
                 player_1_info: MatchStatisticPlayerInfo,
                 player_2_info: MatchStatisticPlayerInfo):
        self.match_id = match_id
        self.location_name = location_name
        self.start_date_time = start_date_time
        self.duration = duration
        self.player_1_info = player_1_info
        self.player_2_info = player_2_info

    @property
    def duration_as_str(self):
        return DatetimeUtils.to_hhmm_diff(self.duration)


class MatchStatisticsProvider:
    def __init__(self, date_time_shift: timedelta):
        self.__date_time_shift = date_time_shift

    def list(self) -> list[MatchStatistic]:
        with app.app_context():
            result: list[MatchStatistic] = []

            db_entities = SingleMatchStatistic.query.order_by(SingleMatchStatistic.start_date_time.desc()).all()

            for dbEntity in db_entities:
                player_1_info = MatchStatisticPlayerInfo(
                    id=dbEntity.player_1_id,
                    name=dbEntity.player_1.name,
                    game_won_count=dbEntity.player_1_game_won_count,
                    point_won_count=dbEntity.player_1_point_won_count
                )

                player_2_info = MatchStatisticPlayerInfo(
                    id=dbEntity.player_2_id,
                    name=dbEntity.player_2.name,
                    game_won_count=dbEntity.player_2_game_won_count,
                    point_won_count=dbEntity.player_2_point_won_count
                )

                if player_1_info.id > player_2_info.id:
                    player_1_info, player_2_info = player_2_info, player_1_info

                result.append(MatchStatistic(
                    match_id=dbEntity.match_id,
                    location_name=dbEntity.location.name,
                    start_date_time=dbEntity.start_date_time + self.__date_time_shift,
                    duration=dbEntity.end_date_time - dbEntity.start_date_time,
                    player_1_info = player_1_info,
                    player_2_info=player_2_info
                ))

            return result
