from typing import Annotated

from fastapi import Depends, HTTPException
from pydantic_extra_types.language_code import LanguageAlpha2
from starlette.status import HTTP_404_NOT_FOUND

from app.datbase.repository.CityRepo import CityRepo
from app.datbase.repository.GeoNameRepo import GeoNameRepo
from app.datbase.repository.LocationRepo import LocationRepo
from app.datbase.repository.RoomRepo import RoomRepo
from app.datbase.repository.RoomTranslationRepo import RoomTranslationRepo
from app.schemas.requests import PlaceAdd
from app.service.RoomService import RoomService


class PlaceService:
    def __init__(
            self,
            room_repo: Annotated[RoomRepo, Depends()],
            city_repo: Annotated[CityRepo, Depends()],
            geo_name_repo: Annotated[GeoNameRepo, Depends()],
            location_repo: Annotated[LocationRepo, Depends()],
            room_translation_repo: Annotated[RoomTranslationRepo, Depends()]
    ) -> None:
        self.room_repo = room_repo
        self.city_repo = city_repo
        self.geo_name_repo = geo_name_repo
        self.location_repo = location_repo
        self.room_translation_repo = room_translation_repo

    async def get_place_by_name(self, place_name: str, language: LanguageAlpha2 | None = None):
        url_safe_place = RoomService.sanitize_input(place_name)
        city = await self.city_repo.get_place_by_name(url_safe_place)
        if city is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Place `{place_name}` as: `{url_safe_place}` not found!")

        print(city.lng_min, city.lng_max, city.lat_min, city.lat_max)
        rooms = await self.room_repo.get_by_bbox(city.lng_min, city.lng_max, city.lat_min, city.lat_max)

        return rooms

    async def create_place(self, place: PlaceAdd):
        city_data = {
            "lat": place.lat,
            "lng": place.lng,
            "lat_min": place.lat_min,
            "lat_max": place.lat_max,
            "lng_min": place.lng_min,
            "lng_max": place.lng_max,
            "population": place.population,
            "importance": place.importance,
            "category": place.category,
            "region": place.region,
            "country": place.country,
        }

        db_city = await self.city_repo.create(**city_data)

        for geo_name in place.geo_names:
            geo_name_data = {
                "city_id": db_city.id,
                "name": geo_name.name,
                "name_ascii": RoomService.sanitize_input(geo_name.name),
                "country": place.country,
                "lang": geo_name.lang,
            }

            await self.geo_name_repo.create(**geo_name_data)
        return None

    # @staticmethod
    # def url_safe_name(text: str) -> str:
    #     safe_name = unidecode(unidecode(text))
    #     return re.sub("[^a-z0-9-]", "", safe_name.lower().replace(" ", "-"))
