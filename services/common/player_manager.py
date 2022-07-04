from typing import Optional
from app import app
from database.models import Player as PlayerDb, Tournament as TournamentDb
from models.player import Player


class PlayerManager:
    def __init__(self, db):
        self.__db = db

    def list_all(self) -> list[Player]:
        with app.app_context():
            return [Player(player.id, player.name, player.telegram_id) for player in PlayerDb.query.all()]

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
            return [Player(player.id, player.name, player.telegram_id) for player in
                    PlayerDb.query.filter(~PlayerDb.id.in_(player_in_tournament_ids)).order_by(PlayerDb.id)]
