from datetime import timedelta
from app import app
from database.models import Tournament, SingleMatchStatistic
from enums.match_result import MatchResult
from models.single_match_telegram_statistic import SingleMatchTelegramStatistic
from utils.datetime_utils import DatetimeUtils


class SingleMatchTelegramStatisticProvider:
    def __init__(self, db, time_shift: timedelta):
        self.__db = db
        self.__time_shift = time_shift

    def ensure_and_get(self, tournament_id: int) -> SingleMatchTelegramStatistic:
        with app.app_context():
            tournament = Tournament.query.filter_by(id=tournament_id).first()
            match = tournament.matches[0]
            games = tournament.matches[0].games
            player_1 = tournament.teams[0].players[0]
            player_2 = tournament.teams[1].players[0]
            statistic = SingleMatchStatistic.query.filter_by(tournament_id=tournament_id, match_id=match.id).first()
            if statistic is None:
                player_1_won_game_count = 0
                player_2_won_game_count = 0
                player_1_won_point_count = 0
                player_2_won_point_count = 0

                for game in games:
                    if game.team_1_score > game.team_2_score:
                        player_1_won_game_count += 1
                    elif game.team_1_score < game.team_2_score:
                        player_2_won_game_count += 1
                    else:
                        player_1_won_game_count += 1
                        player_2_won_game_count += 1
                    player_1_won_point_count += game.team_1_score
                    player_2_won_point_count += game.team_2_score

                statistic = SingleMatchStatistic(
                    location_id=tournament.location_id,
                    tournament_id=tournament_id,
                    match_id=match.id,
                    start_date_time=match.start_date_time,
                    end_date_time=match.end_date_time,
                    player_1_id=player_1.id,
                    player_2_id=player_2.id,
                    player_1_game_won_count=player_1_won_game_count,
                    player_2_game_won_count=player_2_won_game_count,
                    player_1_point_won_count=player_1_won_point_count,
                    player_2_point_won_count=player_2_won_point_count
                )

                self.__db.session.add(statistic)
                self.__db.session.commit()

            if statistic.player_1_game_won_count > statistic.player_2_game_won_count:
                result = MatchResult.FIRST_PLAYER_WON
            elif statistic.player_1_game_won_count < statistic.player_2_game_won_count:
                result = MatchResult.SECOND_PLAYER_WON
            else:
                result = MatchResult.DRAW

            tg_text = '🏓 <b>Результаты матча 🏓</b>\n\n'

            tg_text += f'<b>{tournament.location.name}</b>\n'
            tg_text += f'<b>{player_1.name} - {player_2.name}</b>\n'
            tg_text += f'{DatetimeUtils.to_ddmmyyyy_hhmm(statistic.start_date_time, self.__time_shift)} - ' \
                    f'{DatetimeUtils.to_ddmmyyyy_hhmm(statistic.end_date_time, self.__time_shift)}\n\n'

            tg_text += f'<b>Продолжительность:</b> {DatetimeUtils.to_hhmm_diff(statistic.end_date_time - statistic.start_date_time)}\n\n'

            tg_text += '<b>Счет по геймам:</b>\n'
            tg_text += f'{player_1.name} {statistic.player_1_game_won_count} - {statistic.player_2_game_won_count} {player_2.name}\n\n'

            tg_text += '<b>Всего очков:</b>\n'
            tg_text += f'{player_1.name} {statistic.player_1_point_won_count} - {statistic.player_2_point_won_count} {player_2.name}\n\n'

            tg_text += f'<b>Геймы</b> ({player_1.name} - {player_2.name}):\n'
            for game in games:
                tg_text += f'{game.team_1_score} - {game.team_2_score}\n'

            return SingleMatchTelegramStatistic(
                result=result,
                player_1_id=player_1.id,
                player_2_id=player_2.id,
                player_1_telegram_id=player_1.telegram_id,
                player_2_telegram_id=player_2.telegram_id,
                player_1_games_won=statistic.player_1_game_won_count,
                player_2_games_won=statistic.player_2_game_won_count,
                player_1_points_won=statistic.player_1_point_won_count,
                player_2_points_won=statistic.player_2_point_won_count,
                description=tg_text
            )
