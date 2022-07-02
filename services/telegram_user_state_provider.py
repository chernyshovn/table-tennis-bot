from typing import Optional
from app import app
from database.models import TelegramUserState as TelegramUserStateDb
from enums.telegram_user_state import TelegramUserState


class TelegramUserStateProvider:
    def __init__(self, db):
        self.__db = db

    def get(self, id: int) -> Optional[TelegramUserState]:
        with app.app_context():
            entity = TelegramUserStateDb.query.filter_by(id=id).first()
            return entity.value if entity else None

    def set(self, id: int, value: Optional[TelegramUserState]) -> None:
        with app.app_context():
            entity = TelegramUserStateDb.query.filter_by(id=id).first()

            if entity:
                if not value:
                    self.__db.session.delete(entity)
                else:
                    entity.value = value
                    self.__db.session.add(entity)
            else:
                entity = TelegramUserStateDb(id=id, value=value)
                self.__db.session.add(entity)

            self.__db.session.commit()
