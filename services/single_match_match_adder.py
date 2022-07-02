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

    def get_active_id(self, telegram_user_id: int) -> int:
        with app.app_context():
            match = Match.query.filter_by(initiator_telegram_user_id=telegram_user_id, end_date_time=None).first()
            return match.id if match else None

    def finish_match(self, id: int):
        with app.app_context():
            match = Match.query.filter_by(id=id).first()
            if match:
                match.end_date_time = datetime.utcnow()
                self.__db.session.add(match)
                self.__db.session.commit()
