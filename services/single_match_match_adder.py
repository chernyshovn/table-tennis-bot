from datetime import datetime
from database.models import Tournament, Match
from app import app


class SingleMatchMatchAdder:
    def __init__(self, db):
        self.__db = db

    def add(self, tournament_id: int) -> int:
        with app.app_context():
            tournament = Tournament.query.filter_by(id=tournament_id).first()
            match = Match(
                initiator_telegram_user_id=tournament.initiator_telegram_user_id,
                team_1_id=tournament.teams[0].id,
                team_2_id=tournament.teams[1].id,
                start_date_time=datetime.utcnow()
            )
            tournament.matches.append(match)
            self.__db.session.add(tournament)
            self.__db.session.commit()
            return match.id
