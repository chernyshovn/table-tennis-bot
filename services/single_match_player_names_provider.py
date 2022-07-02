from database.models import Match
from app import app


class SingleMatchPlayerNameProvider:
    def __init__(self, db):
        self.__db = db

    def get(self, match_id) -> list[str]:
        with app.app_context():
            match = Match.query.filter_by(id=match_id).first()
            return [
                match.team_1.players[0].name,
                match.team_2.players[0].name
            ]
