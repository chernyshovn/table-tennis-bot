from datetime import datetime
from database.models import Match, Game
from app import app


class SingleMatchGameAdder:
    def __init__(self, db):
        self.__db = db

    def add(self, telegram_user_id: int, player_1_score: int, player_2_score: int) -> int:
        with app.app_context():
            match = Match.query.filter_by(initiator_telegram_user_id=telegram_user_id, end_date_time=None).first()

            game = Game(
                match_id=match.id,
                team_1_score=player_1_score,
                team_2_score=player_2_score,
                date_time=datetime.utcnow()
            )

            self.__db.session.add(game)
            self.__db.session.commit()
