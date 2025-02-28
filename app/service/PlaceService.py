from typing import Annotated

from fastapi import Depends, HTTPException
from pydantic import IPvAnyAddress
from pydantic_extra_types.coordinate import Latitude, Longitude
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.config import get_settings
from app.database.repository.CityRepo import CityRepo
from app.database.repository.GeoNameRepo import GeoNameRepo
from app.database.repository.LocationRepo import LocationRepo
from app.database.repository.RoomRepo import RoomRepo
from app.database.repository.RoomTranslationRepo import RoomTranslationRepo
from app.schemas.requests import PlaceAdd
from app.shared.city_inflect import PolishCityInflector
from app.shared.text_utils import sanitize_location_input

settings = get_settings()


class PlaceService:
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

    async def get_nearby_cities(self, city_ascii_name: str):
        db_city = await self.city_repo.get_place_by_name(city_ascii_name, LanguageAlpha2("pl"))
        if db_city is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"City `{city_ascii_name} not found!")

        db_nearby_cities = await self.city_repo.get_closest_cities(db_city.lat, db_city.lon, LanguageAlpha2("pl"))
        # Convert the data to a serializable format
        cities_serialized = [
            {
                "name": city[0],
                "lat": float(city[1]),  # Convert Decimal to float
                "lon": float(city[2]),  # Convert Decimal to float
                "importance": float(city[3])  # Convert importance to float if necessary
            }
            for city in db_nearby_cities
        ]

        # Now cities_serialized is a list of dictionaries that can be easily serialized to JSON
        return cities_serialized

    async def get_city_details(self, city_ascii_name: str, language: LanguageAlpha2, country: CountryAlpha2):
        city_and_name = await self.city_repo.get_details_by_ascii_name(city_ascii_name, language, country)
        if city_and_name is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"City `{city_ascii_name}` in {country} for {language} not found!")

        # Example usage

        if city_and_name:
            city, geo_name = city_and_name

            return {
                "city_name": geo_name.name,
                "city_name_inflect": PolishCityInflector().inflect(geo_name.name, "locative"),
                "lat": city.lat,
                "lon": city.lon,
                "lat_min": city.lat_min,
                "lon_min": city.lon_min,
                "lat_max": city.lat_max,
                "lon_max": city.lon_max,
                "population": city.population,
                "importance": city.importance,
                "category": city.category,
                "region": city.region,
                "country": city.country,
                "seo_title": city.seo_title,
                "seo_description": city.seo_description,
            }

        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Name for `{city_ascii_name}` in {country} for {language} not found!")

    async def get_rooms_by_location(self, place_name: str, language: LanguageAlpha2 | None = None):
        url_safe_place = sanitize_location_input(place_name)
        city = await self.city_repo.get_place_by_name(url_safe_place)
        if city is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Place `{place_name}` as: `{url_safe_place}` not found!")

        rooms, counter = await self.room_repo.get_by_bbox(city.lon_min, city.lon_max, city.lat_min, city.lat_max, ["translations"])

        if counter == 0:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Locations `{place_name}` as: `{url_safe_place}` has no ER rooms")

        lang_code = language
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

        latitude = Latitude("50.24230")
        longitude = Longitude("19.13851")

        rooms = await self.room_repo.get_nearby_rooms(latitude, longitude, 50, ["translations"])

        lang_code = "pl"
        for room in rooms:
            translation = next((t for t in room.translations if t.lang == lang_code.lower()), None)
            room.translation = translation if translation else None
        return rooms

    async def get_places_with_rooms(self, country: CountryAlpha2):
        places = await self.location_repo.get_places_with_rooms(country)

        places_with_rooms_dict = [
            {"city": city, "ascii_name": sanitize_location_input(city), "state_province": state_province, "room_count": room_count}
            for city, state_province, room_count in places
        ]

        return places_with_rooms_dict

    async def create_place(self, place: PlaceAdd):
        city_data = {
            "name": place.name,
            "name_ascii": sanitize_location_input(place.name),
            "lat": place.lat,
            "lon": place.lon,
            "lat_min": place.lat_min,
            "lat_max": place.lat_max,
            "lon_min": place.lon_min,
            "lon_max": place.lon_max,
            "population": place.population,
            "importance": place.importance,
            "category": place.category,
            "region": place.region,
            "country": place.country,
            "language": place.language,
        }

        db_city = await self.city_repo.create(**city_data)

        for geo_name in place.geo_names:
            geo_name_data = {
                "city_id": db_city.id,
                "name": geo_name.name,
                "name_ascii": sanitize_location_input(geo_name.name),
                "country": place.country,
                "lang": geo_name.lang,
            }

            await self.geo_name_repo.create(**geo_name_data)

        return None
