from typing import Optional
from datetime import datetime
from app import app
from database.models import Player as PlayerDb, Tournament as TournamentDb
from models.player import Player


class PlayerManager:
    def __init__(self, db):
        self.__db = db

    def list_all(self) -> list[Player]:
        with app.app_context():
            return [
                Player(
                    player.id,
                    player.name,
                    player.telegram_id,
                    player.is_active,
                    player.creation_date_time
                )
                for player in PlayerDb.query.all()
            ]

    def get_name_by_id(self, id: int) -> Optional[str]:
        with app.app_context():
            entity = PlayerDb.query.filter_by(id=id).first()
            return entity.name if entity else None

    def list_not_in_tournament(self, tournament_id: int) -> list[Player]:
        with app.app_context():
            tournament = TournamentDb.query.filter_by(id=tournament_id).first()
            player_in_tournament_ids = []
            for team in tournament.teams:
                for player in team.players:
                    player_in_tournament_ids.append(player.id)
            return [
                Player(
                    player.id,
                    player.name,
                    player.telegram_id,
                    player.is_active,
                    player.creation_date_time
                )
                for player in PlayerDb.query.filter(
                    ~PlayerDb.id.in_(player_in_tournament_ids),
                    PlayerDb.is_active
                ).order_by(PlayerDb.id)
            ]

    def get_by_name(self, name: str) -> Optional[Player]:
        with app.app_context():
            player = PlayerDb.query.filter(PlayerDb.name.ilike(name)).first()
            if player:
                return Player(
                    player.id,
                    player.name,
                    player.telegram_id,
                    player.is_active,
                    player.creation_date_time
                )
            return None

    def update_is_active(self, id: int, is_active: bool):
        with app.app_context():
            entity = PlayerDb.query.get(id)
            if entity.is_active != is_active:
                entity.is_active = is_active
                self.__db.session.add(entity)
                self.__db.session.commit()

    def create(self, name: str) -> None:
        with app.app_context():
            entity = PlayerDb(
                name=name,
                telegram_id=None,
                is_active=True,
                creation_date_time=datetime.utcnow()
            )
            self.__db.session.add(entity)
            self.__db.session.commit()
