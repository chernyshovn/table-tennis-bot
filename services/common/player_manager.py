from typing import List, Optional
from app import app
from database.models import Player as PlayerDb
from models.player import Player


class PlayerManager:
    def __init__(self, db):
        self.__db = db

    def list_all(self) -> List[Player]:
        with app.app_context():
            return [Player(player.id, player.name, player.telegram_id) for player in PlayerDb.query.all()]

    def get_name_by_id(self, id: int) -> Optional[str]:
        with app.app_context():
            entity = PlayerDb.query.filter_by(id=id).first()
            return entity.name if entity else None
