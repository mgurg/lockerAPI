from typing import Annotated

from fastapi import Depends, HTTPException
from pydantic import IPvAnyAddress
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2
from starlette.status import HTTP_404_NOT_FOUND

from app.config import get_settings
from app.datbase.repository.CityRepo import CityRepo
from app.datbase.repository.GeoNameRepo import GeoNameRepo
from app.datbase.repository.LocationRepo import LocationRepo
from app.datbase.repository.RoomRepo import RoomRepo
from app.datbase.repository.RoomTranslationRepo import RoomTranslationRepo
from app.schemas.requests import PlaceAdd
from app.service.RoomService import RoomService

settings = get_settings()


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

    async def get_rooms_by_location(self, place_name: str, language: LanguageAlpha2 | None = None):
        url_safe_place = RoomService.sanitize_input(place_name)
        city = await self.city_repo.get_place_by_name(url_safe_place)
        if city is None:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Place `{place_name}` as: `{url_safe_place}` not found!"
            )

        print(city.lng_min, city.lng_max, city.lat_min, city.lat_max)
        rooms = await self.room_repo.get_by_bbox(
            city.lng_min,
            city.lng_max,
            city.lat_min,
            city.lat_max,
            ["translations"]
        )

        lang_code = "pl"
        for room in rooms:
            translation = next((t for t in room.translations if t.lang == lang_code.lower()), None)
            room.translation = translation if translation else None
        return rooms

    async def get_rooms_by_ip(self, ip: IPvAnyAddress):
        # api_key = settings.API_KEY_IPGEOLOCATION
        # url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={ip}"
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(url)
        #     geo_data =  response.json()
        print(ip)

        latitude = float('50.24230')
        longitude = float('19.13851')

        rooms = await self.room_repo.get_nearby_rooms(latitude, longitude, ["translations"])

        lang_code = "pl"
        for room in rooms:
            translation = next((t for t in room.translations if t.lang == lang_code.lower()), None)
            room.translation = translation if translation else None
        return rooms

    async def get_places_with_rooms(self, country: CountryAlpha2):
        places = await self.location_repo.get_places_with_rooms(country)

        places_with_rooms_dict = [
            {
                "city": city,
                "ascii_name": RoomService.sanitize_input(city),
                "state_province": state_province,
                "room_count": room_count
            }
            for city, state_province, room_count in places
        ]

        return places_with_rooms_dict

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
