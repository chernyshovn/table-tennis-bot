from typing import List, Optional
from app import app
from database.models import Location as LocationDb
from models.location import Location


class LocationRepository:
    def __init__(self, db):
        self.__db = db

    def list_all(self) -> List[Location]:
        with app.app_context():
            return [Location(location.id, location.name) for location in LocationDb.query.all()]

    def get_name_by_id(self, id: int) -> Optional[str]:
        with app.app_context():
            entity = LocationDb.query.filter_by(id=id).first()
            return entity.name if entity else None
