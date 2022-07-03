from app import app
from database.models import Tournament
from models.match_statistic import MatchStatistic, MatchResult


class SingleMatchStatisticProvider:
    def __init__(self, db):
        self.__db = db

    def get(self, tournament_id: int) -> MatchStatistic:
        with app.app_context():
            tournament = Tournament.query.filter_by(id=tournament_id).first()
            games = tournament.matches[0].games
            player_1 = tournament.teams[0].players[0]
            player_2 = tournament.teams[1].players[0]
            player_1_won_game_count = 0
            player_2_won_game_count = 0
            player_1_won_point_count = 0
            player_2_won_point_count = 0

            for game in games:
                if game.team_1_score > game.team_2_score:
                    player_1_won_game_count += 1
                else:
                    player_2_won_game_count += 1
                player_1_won_point_count += game.team_1_score
                player_2_won_point_count += game.team_2_score

            if player_1_won_game_count > player_2_won_game_count:
                result = MatchResult.FIRST_PLAYER_WON
            elif player_1_won_game_count < player_2_won_game_count:
                result = MatchResult.SECOND_PLAYER_WON
            else:
                result = MatchResult.DRAW

            text = '🏓 <b>Результаты игры 🏓</b>\n\n'
            text += f'<b>tournament.location.name</b>/n/n'

            # todo datetime

            text += '<b>Счет по геймам:</b>\n'
            text += f'{player_1.name} {player_1_won_game_count} - {player_2_won_game_count} {player_2.name}\n\n'

            text += '<b>Всего очков:</b>\n'
            text += f'{player_1.name} {player_1_won_point_count} - {player_2_won_point_count} {player_2.name}\n\n'

            text += f'<b>Геймы</b> ({player_1.name} - {player_2.name}):\n'
            for game in games:
                text += f'{game.team_1_score} - {game.team_2_score}\n'

            return MatchStatistic(
                result=result,
                player_1_telegram_id=player_1.telegram_id,
                player_2_telegram_id=player_2.telegram_id,
                description=text
            )
