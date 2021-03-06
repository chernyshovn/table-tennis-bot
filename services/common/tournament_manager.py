from typing import Optional
from datetime import datetime
from app import app
from database.models import Tournament


class TournamentManager:
    def __init__(self, db):
        self.__db = db

    def has_active(self, telegram_user_id: int) -> bool:
        with app.app_context():
            entity = Tournament.query.filter_by(initiator_telegram_user_id=telegram_user_id, end_date_time=None).first()
            return entity is not None

    def get_active_id(self, telegram_user_id: int) -> Optional[int]:
        with app.app_context():
            entity = Tournament.query.filter_by(initiator_telegram_user_id=telegram_user_id, end_date_time=None).first()
            return entity.id if entity else None

    def set_end_date_time(self, id: int):
        with app.app_context():
            entity = Tournament.query.filter_by(id=id).first()
            entity.end_date_time = datetime.utcnow()
            self.__db.session.commit()

    def create(self, location_id: int, initiator_telegram_user_id: int) -> None:
        with app.app_context():
            entity = Tournament(
                location_id=location_id,
                initiator_telegram_user_id=initiator_telegram_user_id,
                start_date_time=datetime.utcnow(),
                end_date_time=None)

            self.__db.session.add(entity)
            self.__db.session.commit()

    def delete(self, id: int) -> None:
        with app.app_context():
            entity = Tournament.query.get(id)
            self.__db.session.delete(entity)
            self.__db.session.commit()
