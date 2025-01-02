from typing import Annotated

from fastapi import Depends
from geopy.distance import geodesic
from pydantic_extra_types.coordinate import Latitude, Longitude

from app.config import get_settings
from app.database.repository.CityRepo import CityRepo
from app.database.repository.GeoNameRepo import GeoNameRepo
from app.database.repository.LocationRepo import LocationRepo
from app.database.repository.RoomRepo import RoomRepo
from app.database.repository.RoomTranslationRepo import RoomTranslationRepo

settings = get_settings()


class CityService:
    def __init__(
        self,
        room_repo: Annotated[RoomRepo, Depends()],
        city_repo: Annotated[CityRepo, Depends()],
        geo_name_repo: Annotated[GeoNameRepo, Depends()],
        location_repo: Annotated[LocationRepo, Depends()],
        room_translation_repo: Annotated[RoomTranslationRepo, Depends()],
    ) -> None:
        self.room_repo = room_repo
        self.city_repo = city_repo
        self.geo_name_repo = geo_name_repo
        self.location_repo = location_repo
        self.room_translation_repo = room_translation_repo

    async def get_closest_cities_with_rooms(self, lat: Latitude = 52.0, lon: Longitude = 19.0):
        cities = await self.city_repo.get_closest_cities(lat, lon)

        cities_with_distance = [
            (
                geo_name.name,
                city.importance,
                geodesic((lat, lon), (city.lat, city.long)).kilometers
            )
            for geo_name, city in cities
        ]
        cities_with_distance.sort(key=lambda x: x[2])  # Sort by distance
        return cities_with_distance[:5]
