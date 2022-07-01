from database.models import Tournament, Team, Player
from app import app


class SingleMatchPlayerAdder:
    def __init__(self, db):
        self.__db = db

    def add(self, tournament_id: int, player_id: int) -> None:
        with app.app_context():
            tournament = Tournament.query.filter_by(id=tournament_id).first()
            player = Player.query.filter_by(id=player_id).first()
            team = Team(name=None)
            team.players.append(player)
            tournament.teams.append(team)
            self.__db.session.add(tournament)
            self.__db.session.commit()
