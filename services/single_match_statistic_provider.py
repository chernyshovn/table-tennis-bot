from app import app
from database.models import Tournament


class SingleMatchStatisticProvider:
    def __init__(self, db):
        self.__db = db

    def get(self, tournament_id: int) -> str:
        with app.app_context():
            tournament = Tournament.query.filter_by(id=tournament_id).first()
            player_1_name = tournament.teams[0].players[0].name
            player_2_name = tournament.teams[1].players[0].name
            player_1_won_games_number = 0
            player_2_won_games_number = 0
            player_1_won_points_number = 0
            player_2_won_points_number = 0
            games = tournament.matches[0].games

            for game in games:
                if game.team_1_score > game.team_2_score:
                    player_1_won_games_number += 1
                else:
                    player_2_won_games_number += 1
                player_1_won_points_number += game.team_1_score
                player_2_won_points_number += game.team_2_score

            result = '<b>Результаты игры!</b>\n\n'

            result += '<b>Счет по геймам:</b>\n'
            result += f'{player_1_name} {player_1_won_games_number} - {player_2_won_games_number} {player_2_name}\n\n'

            result += '<b>Всего очков:</b>\n'
            result += f'{player_1_name} {player_1_won_points_number} - {player_2_won_points_number} {player_2_name}\n\n'

            result += f'<b>Геймы</b> ({player_1_name} - {player_2_name}):\n'
            for game in games:
                result += f'{game.team_1_score} - {game.team_2_score}\n'

            return result
