from datetime import datetime
from database.models import Tournament


class TournamentRepository:
    def __init__(self, db):
        self.__db = db

    def has_active(self, telegram_user_id: int) -> bool:
        tournament = Tournament.query.filter_by(initiator_telegram_user_id=telegram_user_id, end_date_time=None).first()
        return tournament is not None

    def create(self, location_id: int, initiator_telegram_user_id: int) -> None:
        entity = Tournament(
            location_id=location_id,
            initiator_telegram_user_id=initiator_telegram_user_id,
            start_date_time=datetime.utcnow(),
            end_date_time=None)

        self.__db.session.add(entity)
        self.__db.session.commit()

