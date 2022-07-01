from typing import List
from database.models import Location as LocationDb
from models.location import Location


class LocationRepository:
    def __init__(self, db):
        self.__db = db

    def list_all(self) -> List[Location]:
        return [Location(location.id, location.name) for location in LocationDb.query.all()]